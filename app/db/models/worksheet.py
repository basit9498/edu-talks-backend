from app.db.base import Base
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
import enum


class WorkSheetTypeEnum(str, enum.Enum):
    all = "all"
    fill_in_the_blank = "fill_in_the_blank"
    mcqs = "mcqs"
    short_question = "short_question"
    long_answer = "long_answer"


class WorkSheetVisibilityEnum(str, enum.Enum):
    public = "public"
    private = "private"


class WorkSheet(Base):

    # Table
    __tablename__ = "worksheets"

    # attributes
    id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    name = Column(String(255), nullable=False, unique=False)
    type = Column(
        Enum(WorkSheetTypeEnum), nullable=False, default=WorkSheetTypeEnum.all
    )
    visibility = Column(
        Enum(WorkSheetVisibilityEnum),
        default=WorkSheetVisibilityEnum.private,
        nullable=False,
    )

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
    user = relationship("User", back_populates="worksheets")
