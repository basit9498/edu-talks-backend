from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.worksheet import WorksheetCreateSchema
from app.services.worksheet import WorkSheetService


worksheet_router = APIRouter(prefix="/worksheet", tags=["WorkSheet"])

# class instance
worksheet_service = WorkSheetService()


@worksheet_router.post("/", status_code=status.HTTP_201_CREATED)
def create_worksheet(
    payload: WorksheetCreateSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    worksheet = worksheet_service.create_worksheet(payload, user, db)
    return {
        "success": True,
        "message": "Worksheet Create successfully",
        "data": worksheet,
    }


@worksheet_router.get("/", status_code=status.HTTP_201_CREATED)
def list_worksheet(db: Session = Depends(get_db), user=Depends(get_current_user)):
    worksheet_list = worksheet_service.worksheet_list(user, db)
    return {"success": True, "data": worksheet_list}


@worksheet_router.get("/{id}/paper-list/", status_code=status.HTTP_200_OK)
def worksheet_paper_list(
    id: str, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    worksheet_paper_list = worksheet_service.worksheet_paper_list(id, db)
    return {"success": True, "data": worksheet_paper_list}
