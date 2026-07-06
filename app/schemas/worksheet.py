from pydantic import BaseModel
from typing import Optional
from app.db.models.worksheet import WorkSheetTypeEnum,WorkSheetVisibilityEnum

class WorksheetCreateSchema(BaseModel):
     
     name:str
     type:WorkSheetTypeEnum 
     visibility:WorkSheetVisibilityEnum = WorkSheetVisibilityEnum.private


     model_config = {
        "use_enum_values": True
    }
