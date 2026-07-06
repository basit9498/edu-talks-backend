from sqlalchemy.orm import Session, contains_eager
from app.db import models
from app.schemas.paper import PaperCreateSchema
from fastapi import HTTPException, status
from sqlalchemy import asc


class PaperService:

    def create_paper(self, payload: PaperCreateSchema, db: Session):
        data = payload.model_dump()

        new_paper = models.Paper(**data)
        db.add(new_paper)
        db.commit()
        db.refresh(new_paper)

        if not new_paper.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paper not created successfully",
            )

        return new_paper

    def create_paper_questions(self, payload_list: list, paper_id: str, db: Session):

        paper_objects = []

        for item in payload_list:

            # Convert Pydantic model → dict (supports both v1 & v2)
            data_dict = (
                item.model_dump() if hasattr(item, "model_dump") else item.dict()
            )

            # Force assign paper_id
            data_dict["paper_id"] = paper_id

            # Create ORM object
            paper_objects.append(models.PaperQuestion(**data_dict))

        db.add_all(paper_objects)
        db.commit()

        for obj in paper_objects:
            db.refresh(obj)

        return paper_objects

    def paper_question_list(self, id: str, db: Session):
        # paper id i have so need all questions
        paper_question_list = (
            db.query(models.Paper)
            .outerjoin(
                models.PaperQuestion, models.PaperQuestion.paper_id == models.Paper.id
            )
            .options(contains_eager(models.Paper.paper_questions))
            .filter(models.Paper.id == id)
            .order_by(asc(models.Paper.created_at))
            .all()
        )
        if not paper_question_list:
            return None

        return paper_question_list[0]
