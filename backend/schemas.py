from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CVBase(BaseModel):
    filename: str
    file_size: int
    upload_time: datetime
    summary_pros: Optional[str] = None
    summary_cons: Optional[str] = None

class CVResponse(CVBase):
    id: int
    
    class Config:
        from_attributes = True

class CVListResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_time: datetime
    
    class Config:
        from_attributes = True

