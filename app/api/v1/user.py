from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.user import ResponseUserSchema
from app.utils.response import ResponseModel


user_router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@user_router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_model=ResponseModel[ResponseUserSchema],
)
async def user_profile(user=Depends(get_current_user)):
    return ResponseModel(success=True, data=user)
