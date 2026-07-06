from pydantic import BaseModel
from typing import Optional, Text
from app.db.models.discussion import TypeEnum, VisibilityEnum


class DiscussionPostSchema(BaseModel):
    title: str
    description: Optional[str] = None
    type: TypeEnum = TypeEnum.general
    visibility: VisibilityEnum = VisibilityEnum.public
    doc_id: Optional[str] = None

    model_config = {"use_enum_values": True}


class MessagePostSchema(BaseModel):
    content: Text
    discussion_id: str

    model_config = {"use_enum_values": True}
