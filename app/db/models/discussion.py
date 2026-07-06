from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    Text,
    ForeignKey,
    Boolean,
)
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship


class TypeEnum(str, enum.Enum):
    general = "general"
    document = "document"
    link = "link"
    workspace = "workspace"


class VisibilityEnum(str, enum.Enum):
    public = "public"
    private = "private"


class Discussion(Base):
    # table name
    __tablename__ = "discussions"

    # attributes
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(Enum(TypeEnum), nullable=False, default=TypeEnum.general)
    visibility = Column(
        Enum(VisibilityEnum), default=VisibilityEnum.private, nullable=False
    )
    summary = Column(Text, nullable=True)
    summary_token_count = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, server_default="false")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    doc_id = Column(
        UUID(as_uuid=True), ForeignKey("user_uploaded_doc.id"), nullable=True
    )

    user = relationship("User", back_populates="discussions")
    messages = relationship(
        "Message", back_populates="discussion", order_by="asc(Message.created_at)"
    )
    summaries = relationship("DiscussionSummary", back_populates="discussion")
    uploaded_doc = relationship("UserUploadedDoc", back_populates="discussion")

    papers = relationship("Paper", back_populates="discussion")
