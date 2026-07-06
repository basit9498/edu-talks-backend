from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db import models
from app.schemas.message import MessageRecentListSchema
from sqlalchemy import and_, update


class MessageService:
    # save message
    def create_message(self, payload, db: Session):
        message = models.Message(**payload)
        db.add(message)
        db.commit()

        if not message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return True

    def get_latests_messages(self, id: str, db: Session):

        if not id:
            return []

        messages = (
            db.query(models.Message.id, models.Message.content, models.Message.role)
            .filter(models.Message.discussion_id == id)
            .order_by(models.Message.created_at.desc())
            .limit(5)
            .all()
        )

        messages.reverse()
        return [MessageRecentListSchema.model_validate(m) for m in messages]

    def get_all_not_summarized_messages(self, id: str, db: Session):
        messages = (
            db.query(models.Message)
            .filter(
                and_(
                    models.Message.discussion_id == id,
                    models.Message.is_summarized == False,
                )
            )
            .all()
        )
        return messages

    def messages_status_is_summarized(self, ids, db: Session):
        # make query that bulk ids make update
        if not ids:
            return False

        statement = (
            update(models.Message)
            .where(models.Message.id.in_(ids))
            .values(is_summarized=True)
        )

        db.execute(statement)
        db.commit()

        return True
