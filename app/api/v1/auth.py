from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.schemas.user import RegisterSchema, LoginSchema, VerificationSchema
from app.services.user import UserService
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, async_get_db
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.helper.google_auth import oauth
from datetime import timedelta
from app.middleware.auth import get_current_user
from app.config import settings
import httpx

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


# instance
def get_user_service():
    return UserService(UserRepository())


# register
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def user_register(
    body: RegisterSchema,
    service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(async_get_db),
):
    user, error = await service.create_user(db, body)

    if error == "EMAIL_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email is already exist. Try with another email!",
        )
    await db.commit()
    return {"success": True, "data": user}


# login
@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def user_login(
    body: LoginSchema,
    service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(async_get_db),
):

    user, error = await service.user_login(db, body)

    if error == "EMAIL_PASSWORD_INCORRECT":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email and password is incorrect!",
        )

    token = create_access_token(
        {"id": str(user.id), "role": user.role}, timedelta(minutes=10 * 60)
    )

    return {"success": True, "data": {"token": token, "user": user}}


# account verification
# @auth_router.post("/verification", status_code=status.HTTP_200_OK)
# def user_verification(body: VerificationSchema, db: Session = Depends(get_db)):
#     return {"message": "user account verification"}


# forgot password
# @auth_router.post("/forgot-password-email")
# def user_forgot_password_email():
#     return {"message":"user forgot password email "}


# Google connection
@auth_router.get("/google/connect")
async def connect_google(request: Request, user=Depends(get_current_user)):
    redirect_uri = request.url_for("google_callback")
    google_redirect = await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        access_type="offline",
        prompt="consent",
        # scope="email profile",
        scope=(
            "openid email profile "
            "https://www.googleapis.com/auth/calendar "
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents",
        ),
        state=str(user.id),
    )

    # ⬅️ Extract redirect URL
    return JSONResponse({"url": google_redirect.headers["location"]})


# @auth_router.get("/google/callback")
# async def google_callback(
#     request: Request,
#     db: AsyncSession = Depends(async_get_db),
#     service: UserService = Depends(get_user_service),
# ):
#     user_id = request.query_params.get("state")
#     token = await oauth.google.authorize_access_token(request, state=None)

#     # user_info = await oauth.google.parse_id_token(request, token)
#     print("token", token)
#     await service.user_update(
#         db,
#         user_id,
#         google_access_token=token["access_token"],
#         google_refresh_token=token.get("refresh_token"),
#         google_expire_at=token["expires_at"],
#     )
#     await db.commit()

#     return RedirectResponse("http://localhost:5173/dashboard/integrations")


@auth_router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(async_get_db),
    service: UserService = Depends(get_user_service),
):
    # 1. Grab the code and user_id from the URL
    code = request.query_params.get("code")
    user_id = request.query_params.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    # 2. Manual Exchange with Google via HTTPX
    # This bypasses all Authlib session/state errors
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,  # Use your actual ID
        "client_secret": settings.GOOGLE_CLIENT_SECRET,  # Use your actual Secret
        "redirect_uri": str(request.url_for("google_callback")),
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        token_data = response.json()

    if response.status_code != 200:
        print(f"Google Error: {token_data}")
        raise HTTPException(
            status_code=400, detail="Failed to exchange token with Google"
        )

    # 3. Use the token_data to update your user
    # token_data contains: 'access_token', 'refresh_token', 'expires_in', etc.
    await service.user_update(
        db,
        user_id,
        google_connected=True,
        google_access_token=token_data.get("access_token"),
        google_refresh_token=token_data.get("refresh_token"),
        google_expire_at=token_data.get("expires_in"),
    )
    await db.commit()

    return RedirectResponse("http://localhost:5173/dashboard/integrations")
