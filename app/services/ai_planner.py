from app.schemas.ai_planner import (
    AIPlannerCreateSchema,
    AIPlannerResumeSchema,
    ToolUserGoogleCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agent.planner_agent import PlannerAgenticWorkflow
from app.repositories.ai_planner import AIPlannerRepository
from app.db import models
from types import SimpleNamespace
import uuid


class AIPlannerServices:

    def __init__(self, repo: AIPlannerRepository):
        self.repo = repo

    async def get_all_plan(
        self,
        db: AsyncSession,
        user_id: str,
        offset: int,
        limit: int,
        search: str | None,
    ):
        list, count = await self.repo.get_all_plan(
            db,
            user_id,
            offset=offset,
            limit=limit,
            search=search,
        )

        return list, count

    async def get_single_plan(self, db: AsyncSession, user_id: str, id: str):
        data = await self.repo.get_plan_by_id(db, user_id, id)

        return data

    async def create_plan(
        self,
        db: AsyncSession,
        body: AIPlannerCreateSchema,
        user: models.User,
        planner_agentic_workflow: PlannerAgenticWorkflow,
    ):
        new_thread_id = uuid.uuid4()

        result = await planner_agentic_workflow.run_async(
            {
                "user_query": body.user_prompt,
                "user_current_level": body.user_current_level,
                "demand_duration": body.demand_duration,
                "primary_goal": body.primary_goal,
                "user": ToolUserGoogleCredentials(
                    google_access_token=user.google_access_token,
                    google_refresh_token=user.google_refresh_token,
                ),
            },
            config={"configurable": {"thread_id": new_thread_id}},
        )

        payload = dict(
            {
                "title": body.user_prompt,
                "thread_id": new_thread_id,
                "user_id": user.id,
                "roadmap": result["roadmap"]["roadmap"],
            }
        )

        ai_planner_conversation = models.AIPlannerConversation(**payload)
        plan_conversation = await self.repo.create_ai_planner_conversation(
            db, ai_planner_conversation
        )

        return {
            "roadmap": result,
            "thread_id": new_thread_id,
            "plan_conversation_id": plan_conversation.id,
        }

    async def resume_plan(
        self,
        db: AsyncSession,
        body: AIPlannerResumeSchema,
        planner_agentic_workflow: PlannerAgenticWorkflow,
    ):

        result = await planner_agentic_workflow.resume_async(
            {
                "approval_status": body.feedback,
            },
            config={"configurable": {"thread_id": body.thread_id}},
        )

        await self.repo.update_ai_planner_conversation_by_id(
            db=db, thread_id=body.thread_id, roadmap=result["roadmap"]
        )

        return result
