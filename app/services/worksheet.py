from app.schemas.worksheet import WorksheetCreateSchema
from sqlalchemy.orm import Session, aliased
from app.db import models
from fastapi import HTTPException, status
from sqlalchemy import func


class WorkSheetService:

    def create_worksheet(self, payload: WorksheetCreateSchema, user, db: Session):
        data = payload.model_dump()
        data["user_id"] = user.id
        worksheet = models.WorkSheet(**data)
        db.add(worksheet)
        db.commit()
        db.refresh(worksheet)

        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Worksheet not created successfully",
            )

        return worksheet

    def worksheet_list(self, user, db: Session):
        worksheet_list = (
            db.query(models.WorkSheet).filter(models.WorkSheet.user_id == user.id).all()
        )

        return worksheet_list

    def worksheet_paper_list(self, id: str, db: Session):

        worksheet_paper_list = (
            db.query(models.Paper).filter(models.Paper.worksheet_id == id).all()
        )
        return worksheet_paper_list

        # PQ = aliased(models.PaperQuestion)
        # query = (
        #     db.query(models.Paper, func.count(PQ.id).label("question_count"))
        #     .outerjoin(PQ, PQ.paper_id == models.Paper.id)
        #     .filter(models.Paper.worksheet_id == id)
        #     .group_by(models.Paper.id)
        # )

        # papers = query.all()

        # result = []
        # for paper, question_count in papers:
        #     result.append(
        #         {
        #             "id": str(paper.id),
        #             "title": paper.title,
        #             "total_marks": paper.total_marks,
        #             "difficulty_level": paper.difficulty_level,
        #             "passing_percentage": paper.passing_percentage,
        #             "time_limit_minutes": paper.time_limit_minutes,
        #             "source_type": paper.source_type,
        #             "question_setup": paper.question_setup,
        #             "created_at": paper.created_at,
        #             "updated_at": paper.updated_at,
        #             "question_count": question_count,
        #         }
        #     )

        # return result
