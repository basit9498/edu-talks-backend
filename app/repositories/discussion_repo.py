from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy import func, or_
from app.db import models
from typing import List, Tuple


class DiscussionRepository:

    async def get_all_discussion(
        self,
        db: AsyncSession,
        user_id: str,
        offset: int,
        limit: int,
        search: str | None = None,
        type: str | None = None,
    ) -> Tuple[List[models.Discussion], int]:

        base_filter = [
            models.Discussion.user_id == user_id,
            models.Discussion.is_deleted == False,
        ]

        if search:
            search_filter = or_(
                models.Discussion.title.ilike(f"%{search}%"),
                models.Discussion.description.ilike(f"%{search}%"),
            )
            base_filter.append(search_filter)

        if type:
            type_filter = or_(models.Discussion.type == type)
            base_filter.append(type_filter)

        stmt = select(models.Discussion).where(*base_filter).offset(offset).limit(limit)

        query_result = await db.execute(stmt)
        discussions = query_result.scalars().all()

        # count
        count_query = await db.execute(
            select(func.count(models.Discussion.id)).where(*base_filter)
        )
        count = count_query.scalar_one()

        return discussions, count

    # delete discussion
    async def delete_by_id(self, db: AsyncSession, id: str, user_id: str) -> bool:
        stmt = select(models.Discussion).where(
            models.Discussion.id == id, models.Discussion.user_id == user_id
        )

        query_result = await db.execute(stmt)
        discussion = query_result.scalar_one_or_none()

        if not discussion:
            return False

        discussion.is_deleted = True

        # await db.delete(discussion)
        await db.flush()

        return True

    async def get_discussion_with_messages(
        self, db: AsyncSession, id: str, user_id: str
    ):
        stmt = (
            select(models.Discussion)
            .where(
                models.Discussion.id == id,
                models.Discussion.user_id == user_id,
                models.Discussion.is_deleted == False,
            )
            .options(
                selectinload(models.Discussion.messages),
                selectinload(models.Discussion.uploaded_doc).options(
                    load_only(
                        models.UserUploadedDoc.id,
                        models.UserUploadedDoc.name,
                        models.UserUploadedDoc.doc_link,
                    )
                ),
                selectinload(models.Discussion.papers).options(
                    load_only(
                        models.Paper.id,
                        models.Paper.discussion_id,
                        models.Paper.worksheet_id,
                        models.Paper.title,
                    )
                ),
            )
        )

        query_result = await db.execute(stmt)
        return query_result.scalar_one_or_none()
