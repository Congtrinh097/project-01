from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base

class CV(Base):
    __tablename__ = "cvs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    summary_pros = Column(Text, nullable=True)
    summary_cons = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    
    def __repr__(self):
        return f"<CV(id={self.id}, filename='{self.filename}')>"


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    generated_text = Column(Text, nullable=False)
    pdf_path = Column(String(500), nullable=False)
    pdf_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Resume(id={self.id}, filename='{self.pdf_filename}')>"


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    position = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    job_link = Column(String(500), nullable=False)
    location = Column(String(255), nullable=True)
    working_type = Column(String(100), nullable=True)
    skills = Column(JSON, nullable=True)  # Array of skills
    responsibilities = Column(JSON, nullable=True)  # Array of responsibilities
    education = Column(String(255), nullable=True)
    experience = Column(String(255), nullable=True)
    technical_skills = Column(JSON, nullable=True)  # Array of technical skills
    soft_skills = Column(JSON, nullable=True)  # Array of soft skills
    benefits = Column(JSON, nullable=True)  # Array of benefits
    company_size = Column(String(100), nullable=True)
    why_join = Column(JSON, nullable=True)  # Array of why join reasons
    posted = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    summary_embedding = Column(Vector(1536), nullable=True)  # OpenAI embedding for summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Job(id={self.id}, position='{self.position}', company='{self.company}')>"
