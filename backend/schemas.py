from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

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


# Chatbot Schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime


# CV Recommendation Schemas
class CVRecommendRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class CVRecommendResult(BaseModel):
    id: int
    filename: str
    similarity_score: float
    text_preview: str
    summary_pros: Optional[str] = None
    upload_time: Optional[str] = None

class CVRecommendResponse(BaseModel):
    query: str
    results: List[CVRecommendResult]
    ai_recommendation: str


# Job Extraction Schemas
class JobURLs(BaseModel):
    urls: List[str]


# Individual Job Schemas
class JobResponse(BaseModel):
    id: int
    position: str
    company: str
    job_link: str
    location: Optional[str] = None
    working_type: Optional[str] = None
    skills: Optional[List[str]] = []
    responsibilities: Optional[List[str]] = []
    education: Optional[str] = None
    experience: Optional[str] = None
    technical_skills: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    company_size: Optional[str] = None
    why_join: Optional[List[str]] = []
    posted: Optional[datetime] = None
    tags: Optional[List[str]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    id: int
    position: str
    company: str
    location: Optional[str] = None
    working_type: Optional[str] = None
    tags: Optional[List[str]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True