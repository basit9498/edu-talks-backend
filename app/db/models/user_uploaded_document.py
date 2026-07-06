from app.db.base import Base
from sqlalchemy import Column, Boolean, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class UserUploadedDoc(Base):

    __tablename__ = "user_uploaded_doc"

    id = Column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String, nullable=False)
    doc_link = Column(String, nullable=False)
    is_embedded_generated = Column(Boolean, nullable=False, server_default="false")
    is_deleted = Column(Boolean, nullable=False, default=False)

    # timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey(column="users.id"), nullable=False)
    user = relationship("User", back_populates="uploaded_doc")
    discussion = relationship("Discussion", back_populates="uploaded_doc")
