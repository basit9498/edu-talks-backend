from app.db.base import Base
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    Float,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum


# -----------------------------
# ENUM: Attempt Status
# -----------------------------

class AttemptStatus(str,enum.Enum):
    in_progress = "in_progress"
    submitted = "submitted"


# -----------------------------
# PAPER ATTEMPT MODEL
# -----------------------------

class PaperAttempt(Base):

    __tablename__ = "paper_attempts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )



    # When the attempt started
    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Set when attempt is submitted
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Total marks obtained in this attempt
    total_marks_obtained = Column(Float, nullable=True)

    # Optional feedback (AI feedback or manual)
    feedback = Column(String, nullable=True)

    # Attempt status
    status = Column(
        Enum(AttemptStatus, name="attempt_status_enum"),
        nullable=False,
        default=AttemptStatus.in_progress
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


    paper_id = Column(
        UUID(as_uuid=True),
        ForeignKey("papers.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
