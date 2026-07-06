from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, conint
from enum import Enum


# -----------------------------
# Pydantic ENUMS (match exactly with SQLAlchemy enums)
# -----------------------------
class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SourceType(str, Enum):
    discussion = "discussion"
    document = "document"
    discussion_document = "discussion_document"


# -----------------------------
# Schema for each question type in JSONB
# -----------------------------
class QuestionSetupItem(BaseModel):
    type: str = Field(..., description="Type of question (mcq, short, fill_in_the_blank, etc.)")
    number_of_questions: conint(ge=1) = Field(..., description="How many questions of this type")
    total_marks: conint(ge=1) = Field(..., description="Total marks allocated to this type")


# -----------------------------
# CREATE SCHEMA
# -----------------------------
class PaperCreateSchema(BaseModel):
    title: str = Field(..., max_length=255)
    total_marks: conint(ge=1)
    difficulty_level: DifficultyLevel = DifficultyLevel.easy
    passing_percentage: conint(ge=0, le=100)
    time_limit_minutes: conint(ge=1) = 60
    source_type: SourceType

    worksheet_id: UUID
    discussion_id: Optional[UUID] = None

    question_setup: List[QuestionSetupItem]


# -----------------------------
# UPDATE SCHEMA (Partial update allowed)
# -----------------------------
class PaperUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    total_marks: Optional[conint(ge=1)] = None
    difficulty_level: Optional[DifficultyLevel] = None
    passing_percentage: Optional[conint(ge=0, le=100)] = None
    time_limit_minutes: Optional[conint(ge=1)] = None
    source_type: Optional[SourceType] = None

    worksheet_id: Optional[UUID] = None
    discussion_id: Optional[UUID] = None

    question_setup: Optional[List[QuestionSetupItem]] = None


# -----------------------------
# RESPONSE SCHEMA
# -----------------------------
class PaperResponseSchema(BaseModel):
    id: UUID
    title: str
    total_marks: int
    difficulty_level: DifficultyLevel
    passing_percentage: int
    time_limit_minutes: int
    source_type: SourceType
    worksheet_id: UUID
    discussion_id: Optional[UUID]
    question_setup: List[QuestionSetupItem]

    created_at: str
    updated_at: str

    class Config:
        from_attributes = True   # important for SQLAlchemy → Pydantic
