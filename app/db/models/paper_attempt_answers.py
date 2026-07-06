from app.db.base import Base
from sqlalchemy import (
    Column,
    Enum,
    Float,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum


# -----------------------------
# ENUM: Grading Types
# -----------------------------

class GradingType(str,enum.Enum):
    auto = "auto"     # MCQ / True-False / Fill-blanks
    manual = "manual" # Teacher grading
    ai = "ai"         # LLM grading


# -----------------------------
# PAPER ANSWER MODEL
# -----------------------------

class PaperAttemptAnswer(Base):

    __tablename__ = "paper_attempt_answers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

  

    # User answer stored flexibly (text, choices, array, etc.)
    user_answer = Column(JSONB, nullable=True)

    # Auto marked correctness (for MCQ/T/F/fill_blank)
    # null for subjective questions
    is_correct = Column(
    Boolean,
    nullable=True
        
    )

    # Marks scored for this question (auto, manual, or AI)
    marks_obtained = Column(Float, nullable=True)

    # How was this question graded?
    grading_type = Column(
        Enum(GradingType, name="grading_type_enum"),
        nullable=True,
        default=GradingType.auto
    )

     # Timestamps
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


      # Link to attempt
    paper_attempt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("paper_attempts.id", ondelete="CASCADE"),
        nullable=False
    )

    # Link to question definition
    paper_question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("paper_questions.id", ondelete="CASCADE"),
        nullable=False
    )
