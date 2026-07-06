from app.db.base import Base
from sqlalchemy import Column,String,DateTime,Enum,ForeignKey,Text,Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
import enum



class DiscussionSummary(Base):

    # Table
    __tablename__ = "discussion_summaries"

    # attributes
    id = Column(UUID(as_uuid=True),primary_key=True,nullable=False,default=uuid.uuid4)
    content = Column(Text,nullable=False)
    token_count = Column(Integer,nullable=True)

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

    # relationships
    discussion_id = Column(UUID(as_uuid=True),ForeignKey("discussions.id"), nullable=False)
    discussion = relationship("Discussion",back_populates="summaries")