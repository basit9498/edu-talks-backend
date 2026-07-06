from app.db.base import Base
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    DateTime,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum


# -----------------------------
# ENUM DEFINITIONS
# -----------------------------


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SourceType(str, enum.Enum):
    discussion = "discussion"
    document = "document"
    discussion_document = "discussion_document"


# -----------------------------
# PAPER MODEL
# -----------------------------


class Paper(Base):

    __tablename__ = "papers"

    # Primary Key
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Title of the paper
    title = Column(String(255), nullable=False)

    # Total marks of the paper
    total_marks = Column(Integer, nullable=False)

    # Difficulty level (easy / medium / hard)
    difficulty_level = Column(
        Enum(DifficultyLevel, name="difficulty_level_enum"),
        nullable=False,
        default=DifficultyLevel.easy,
    )

    # Passing percentage (0–100)
    passing_percentage = Column(Integer, nullable=False)

    # Time limit in minutes
    time_limit_minutes = Column(Integer, nullable=False, default=60)

    # Source type: discussion, document, discussion+document
    source_type = Column(
        Enum(SourceType, name="paper_source_enum"),
        nullable=False,
    )

    # JSON schema defining question types, count and marks
    # Example:
    # [
    #   {"type": "mcq", "number_of_questions": 5, "total_marks": 2},
    #   {"type": "short", "number_of_questions": 2, "total_marks": 5}
    # ]
    question_setup = Column(JSONB, nullable=False)

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
    # Foreign Keys

    worksheet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("worksheets.id", ondelete="CASCADE"),
        nullable=False,
    )

    discussion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("discussions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # document_id = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("documents.id", ondelete="SET NULL"),
    #     nullable=True
    # )

    paper_questions = relationship("PaperQuestion", back_populates="paper")
    discussion = relationship("Discussion", back_populates="papers")
