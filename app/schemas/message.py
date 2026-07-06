from pydantic import BaseModel
from datetime import datetime

class MessageRecentListSchema(BaseModel):
    content: str
    role: str

    class Config:
        from_attributes = True
