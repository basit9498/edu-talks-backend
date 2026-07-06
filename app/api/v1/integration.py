from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.auth import get_current_user
from app.services.google import (
    get_calendar_service,
    get_drive_doc_service,
    create_folder,
    create_google_doc,
    write_text_to_doc,
    get_or_create_folder,
)
from app.db.session import async_get_db
from app.services.user import UserService
from app.repositories.user_repo import UserRepository
from app.schemas.user import GoogleToolConnectionRequest
from app.db import models


integration_router = APIRouter(
    prefix="/integration",
    tags=["Integration"],
)


# instance
def get_user_service():
    return UserService(UserRepository())


@integration_router.get(
    "/google-calendar/list",
    status_code=status.HTTP_200_OK,
)
async def google_calendar_list(user=Depends(get_current_user)):
    events = get_calendar_service(user).events().list(calendarId="primary").execute()
    return {"list": events}


@integration_router.post(
    "/google-doc/add",
    status_code=status.HTTP_200_OK,
)
async def google_calendar_list(user=Depends(get_current_user)):
    access = get_drive_doc_service(user)
    folder_id = get_or_create_folder(access["drive_service"])
    doc_id = create_google_doc(
        access["docs_service"], access["drive_service"], folder_id
    )
    write_text_to_doc(access["docs_service"], doc_id)

    return {"list": "Done"}


# connection
@integration_router.post("/google-tool-connection", status_code=status.HTTP_200_OK)
async def google_tool_connection(
    body: GoogleToolConnectionRequest,
    db: AsyncSession = Depends(async_get_db),
    user: models.User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.user_update(db, user.id, **body.model_dump(exclude_unset=True))
    await db.commit()
    return {"success": True}
