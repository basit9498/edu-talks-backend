from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, async_get_db
from app.core.security import decode_token
import jwt
from app.services.user import UserService
from app.repositories.user_repo import UserRepository


# instance
def get_user_service():
    return UserService(UserRepository)


async def get_current_user(
    authorization: str = Header(None),
    service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(async_get_db),
):

    print("authorization", authorization)
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token=token)
        user = await service.user_profile(db, payload.get("id"))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token for the current user",
            )

        return user

    except jwt.ExpiredSignatureError:
        print("authorization", "Token is expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired"
        )

    except Exception:
        print("authorization", "Token is invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid"
        )
