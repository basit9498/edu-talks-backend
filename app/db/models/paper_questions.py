from app.db.base import Base
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Enum,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum


# -----------------------------
# ENUM: Question Types
# -----------------------------


class QuestionType(str, enum.Enum):
    #    all = "all"
    fill_in_the_blank = "fill_in_the_blank"
    mcqs = "mcqs"
    short_question = "short_question"
    long_answer = "long_answer"


# -----------------------------
# PAPER QUESTIONS MODEL
# -----------------------------


class PaperQuestion(Base):

    __tablename__ = "paper_questions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )

    # Actual question content
    question = Column(Text, nullable=False)

    # Type: mcq / fill_blank / true_false / short / long
    question_type = Column(
        Enum(QuestionType, name="question_type_enum"), nullable=False
    )

    # Whether the question has a fixed answer
    # true → objective (MCQ, fill_blank)
    # false → subjective (short, long)
    is_fixed_answer = Column(Boolean, nullable=False)

    # Options for MCQs or fill-in (e.g., ["A", "B", "C", "D"])
    question_options = Column(JSONB, nullable=True)

    # Correct answers (may be single or multiple)
    # MCQ: "A"
    # Fill blanks: ["function", "class"]
    correct_answer = Column(JSONB, nullable=True)

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

    # FK → papers.id
    paper_id = Column(
        UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False
    )

    paper = relationship("Paper", back_populates="paper_questions")
