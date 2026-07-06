from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.db import models


class UserRepository:

    async def get_by_email(self, db: AsyncSession, email: str):
        query_result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        return query_result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user: models.User):
        db.add(user)
        await db.flush()
        return user

    async def update_by_id(self, db: AsyncSession, user_id: str, **kwargs):
        stmt = (
            update(models.User)
            .where(models.User.id == user_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)
        await db.flush()
