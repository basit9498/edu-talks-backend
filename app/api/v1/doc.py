from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.middleware.auth import get_current_user
import uuid
import os

from app.services.doc import DocService

doc_router = APIRouter(
    prefix="/doc",
    tags=["Document"],
)


# setting
doc_service = DocService()
UPLOAD_DIR = "app/public/doc"


@doc_router.post("/upload", status_code=status.HTTP_200_OK)
async def uploaded_doc(
    file: UploadFile = File(),
    name: str = Form(),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"

    file_path = os.path.join(UPLOAD_DIR, file_name)

    # Save file locally
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Save DB record
    doc = doc_service.upload_document(
        {
            "name": name,
            "doc_link": f"/public/doc/{file_name}",
            "user_id": user.id,
        },
        db,
    )

    return {"data": doc}


@doc_router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_doc(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    doc = doc_service.get_all_doc(user.id, db)

    return {"data": doc}
