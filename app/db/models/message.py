from app.db.base import Base
from sqlalchemy import Column, String, Text, Enum, DateTime, Integer, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

class MessageRoleEnum (str, enum.Enum):
    system = "system"
    user = "user"
    assistant = "assistant"



class Message(Base):
    # table name
    __tablename__ = "messages"

    # attributes
    id = Column(UUID(as_uuid=True),primary_key=True,nullable=False,default=uuid.uuid4)
    content = Column(Text,nullable=False)
    role = Column(Enum(MessageRoleEnum),nullable=False)
    token_count = Column(Integer,nullable=True)
    is_summarized = Column(Boolean,default=False)

    # timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # relationships
    discussion_id = Column(UUID(as_uuid=True),ForeignKey(column="discussions.id"),nullable=False)
    discussion = relationship("Discussion",back_populates="messages")





