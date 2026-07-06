from sqlalchemy.ext.asyncio import AsyncSession
from app.db import models
from app.schemas.ai_planner import AIPlannerConversationCreateSchema
from sqlalchemy import func, or_, update
from sqlalchemy.future import select


class AIPlannerRepository:
    async def get_all_plan(
        self,
        db: AsyncSession,
        user_id: str,
        offset: int,
        limit: int,
        search: str | None = None,
    ):
        base_filter = [
            models.AIPlannerConversation.user_id == user_id,
        ]
        if search:
            search_filter = or_(
                models.AIPlannerConversation.title.ilike(f"%{search}%"),
            )
            base_filter.append(search_filter)

        stmt = (
            select(models.AIPlannerConversation)
            .where(*base_filter)
            .offset(offset)
            .limit(limit)
        )

        query_result = await db.execute(stmt)
        plan_list = query_result.scalars().all()

        # count
        count_query = await db.execute(
            select(func.count(models.AIPlannerConversation.id)).where(*base_filter)
        )
        count = count_query.scalar_one()

        return plan_list, count

    async def get_plan_by_id(self, db: AsyncSession, user_id: str, id: str):
        base_filter = [
            models.AIPlannerConversation.user_id == user_id,
            models.AIPlannerConversation.id == id,
        ]

        stmt = select(models.AIPlannerConversation).where(*base_filter)

        query_result = await db.execute(stmt)
        plan = query_result.scalar_one()

        return plan

    async def create_ai_planner_conversation(
        self, db: AsyncSession, conversation: models.AIPlannerConversation
    ):
        db.add(conversation)
        await db.flush()
        return conversation

    async def update_ai_planner_conversation_by_id(
        self, db: AsyncSession, thread_id: str, **kwargs
    ):
        stmt = (
            update(models.AIPlannerConversation)
            .where(models.AIPlannerConversation.thread_id == thread_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)
        await db.flush()
