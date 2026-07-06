from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.user import RegisterSchema, LoginSchema
from app.db import models
from fastapi import HTTPException, status
from app.core.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from app.repositories.user_repo import UserRepository


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, db: AsyncSession, payload: RegisterSchema):

        user_exist = await self.repo.get_by_email(db=db, email=payload.email)

        if user_exist:
            return None, "EMAIL_EXISTS"

        data = payload.model_dump()
        data["password"] = hash_password(data["password"])
        user = models.User(**data)

        await self.repo.create(db, user)

        return user, None

    async def user_login(self, db: AsyncSession, payload: LoginSchema):
        data = payload.model_dump()

        user = await self.repo.get_by_email(db, data["email"])

        if not user:
            return None, "EMAIL_PASSWORD_INCORRECT"

        is_password_match = verify_password(data["password"], user.password)

        if not is_password_match:
            return None, "EMAIL_PASSWORD_INCORRECT"

        return user, None

    async def user_profile(self, db: AsyncSession, id: str):
        query = await db.execute(select(models.User).where(models.User.id == id))
        user = query.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
            )
        return user

    async def user_update(self, db: AsyncSession, id: str, **kwargs):
        await self.repo.update_by_id(db, user_id=id, **kwargs)
        return True
