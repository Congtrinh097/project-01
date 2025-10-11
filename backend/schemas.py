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


# Resume Schemas
class ResumeGenerateRequest(BaseModel):
    input_text: str

class ResumeResponse(BaseModel):
    id: int
    generated_text: str
    pdf_filename: str
    download_url: str
    file_size: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeListResponse(BaseModel):
    id: int
    pdf_filename: str
    file_size: int
    created_at: datetime
    
    class Config:
        from_attributes = True
