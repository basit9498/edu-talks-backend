from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class RegisterSchema(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=3, max_length=16)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class VerificationSchema(BaseModel):
    token: str


class ResponseUserSchema(BaseModel):
    id: str
    name: str
    email: str
    is_verified: bool

    @field_validator("id", mode="before")
    def to_string(cls, v):
        return str(v)

    class Config:
        from_attributes = True


class GoogleToolConnectionRequest(BaseModel):
    google_calendar_connected: Optional[bool] = None
    google_drive_connected: Optional[bool] = None
    google_class_room_connected: Optional[bool] = None
