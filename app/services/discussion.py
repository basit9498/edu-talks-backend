from sqlalchemy.orm import Session, contains_eager
from app.schemas.discussion import DiscussionPostSchema
from app.db import models
from fastapi import HTTPException, status
from sqlalchemy import and_, outerjoin, asc
from app.repositories.discussion_repo import DiscussionRepository
from sqlalchemy.ext.asyncio import AsyncSession


class DiscussionService:

    def __init__(self, repo: DiscussionRepository):
        self.repo = repo

    def create_discussion(
        self, payload: DiscussionPostSchema, logged_user, db: Session
    ):
        data = payload.model_dump()
        data["user_id"] = logged_user.id
        discussion = models.Discussion(**data)
        db.add(discussion)
        db.commit()
        db.refresh(discussion)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discussion is not created successfully!",
            )

        return discussion

    async def get_all_discussions(
        self,
        user_id: str,
        offset: int,
        limit: int,
        search: str | None,
        type: str | None,
        db: AsyncSession,
    ):

        discussion_list, count = await self.repo.get_all_discussion(
            db, user_id, offset=offset, limit=limit, search=search, type=type
        )

        return discussion_list, count

    # this is just for temporally uses
    def get_discussion(self, id: str, logged_user, db: Session):
        discussion = (
            db.query(models.Discussion)
            .filter(
                models.Discussion.user_id == logged_user.id, models.Discussion.id == id
            )
            .first()
        )

        return discussion

    async def delete_discussion(self, db: AsyncSession, id: str, user_id: str):
        return await self.repo.delete_by_id(db, id, user_id)

    async def get_single_discussion_with_detail(
        self, db: AsyncSession, id: str, user_id: str
    ):
        return await self.repo.get_discussion_with_messages(db, id, user_id)

    def get_discussion_detail_only(self, id, logged_user, db: Session):
        discussion = (
            db.query(models.Discussion)
            .filter(
                models.Discussion.user_id == logged_user.id, models.Discussion.id == id
            )
            .first()
        )

        return discussion

    def get_simple_discussion(self, id, db: Session):
        discussion = (
            db.query(models.Discussion).filter(models.Discussion.id == id).first()
        )
        return discussion

    def save_discussion_summary(self, payload, db: Session):

        discussion_summary = models.DiscussionSummary(**payload)

        db.add(discussion_summary)
        db.commit()

        db.refresh(discussion_summary)

        return discussion_summary

    def save_summary(self, payload, db: Session):

        # Fetch discussion
        discussion = (
            db.query(models.Discussion)
            .filter(models.Discussion.id == payload["discussion_id"])
            .first()
        )

        # If discussion not found → raise error
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")

        # Update fields safely
        discussion.summary = payload["content"]
        discussion.summary_token_count = payload["token_count"]

        # Commit changes
        db.commit()
        db.refresh(discussion)

        return discussion

    def list_of_summaries(self, id: str, db=Session):
        summaries_list = (
            db.query(models.DiscussionSummary)
            .filter(models.DiscussionSummary.discussion_id == id)
            .all()
        )
        return summaries_list
