from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid


class AIPlannerConversation(Base):
    __tablename__ = "ai_planner_conversations"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    title = Column(String, nullable=True)
    thread_id = Column(UUID(as_uuid=True))
    # roadmap big json file
    roadmap = Column(JSONB, nullable=False, server_default="{}")
    is_completed = Column(
        Boolean, default=False, nullable=False, server_default="false"
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

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

    # relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
