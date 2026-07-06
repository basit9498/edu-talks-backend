from pydantic import BaseModel
from typing import Any, Dict


class AIPlannerCreateSchema(BaseModel):
    user_prompt: str
    user_current_level: str
    demand_duration: str
    primary_goal: str


class AIPlannerResumeSchema(BaseModel):
    thread_id: str
    feedback: str


# class AIPlannerConversationCreateSchema(BaseModel):
#     title: str
#     thread_id: str
#     user_id: str


class AIPlannerConversationCreateSchema(BaseModel):
    title: str
    thread_id: str
    user_id: str
    roadmap: Dict[str, Any]

    class Config:
        orm_mode = True


class ToolUserGoogleCredentials(BaseModel):
    google_access_token: str
    google_refresh_token: str
