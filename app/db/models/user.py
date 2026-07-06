from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, BigInteger
from app.db.base import Base
import enum
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    is_verified = Column(Boolean, default=False)
    # google related
    google_connected = Column(Boolean, nullable=False, server_default="False")
    google_access_token = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)
    google_expire_at = Column(BigInteger, nullable=True)
    google_calendar_connected = Column(Boolean, nullable=False, server_default="False")
    google_drive_connected = Column(Boolean, nullable=False, server_default="False")
    google_class_room_connected = Column(
        Boolean, nullable=False, server_default="False"
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

    # relationship
    discussions = relationship("Discussion", back_populates="user")
    worksheets = relationship("WorkSheet", back_populates="user")
    uploaded_doc = relationship("UserUploadedDoc", back_populates="user")
