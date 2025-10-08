from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
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
    
    def __repr__(self):
        return f"<CV(id={self.id}, filename='{self.filename}')>"

