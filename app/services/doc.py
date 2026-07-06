from sqlalchemy.orm import Session, contains_eager
from app.db import models
from fastapi import HTTPException, status
from sqlalchemy import asc


class DocService:

    def upload_document(self, payload, db: Session):
        new_doc = models.UserUploadedDoc(**payload)
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        return new_doc

    def get_all_doc(self, user_id, db: Session):
        docs = (
            db.query(models.UserUploadedDoc)
            .filter(models.UserUploadedDoc.user_id == user_id)
            .all()
        )
        return docs

    def get_single_doc_detail(self, id: str, db: Session):
        return (
            db.query(models.UserUploadedDoc)
            .filter(models.UserUploadedDoc.id == id)
            .first()
        )

    def update_doc_status(self, id: str, db: Session):
        doc = (
            db.query(models.UserUploadedDoc)
            .filter(models.UserUploadedDoc.id == id)
            .first()
        )

        doc.is_embedded_generated = True

        db.commit()
        db.refresh(doc)

        return doc
