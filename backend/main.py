from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import logging
from datetime import datetime

from database import get_db, engine
from models import Base, CV
from schemas import CVResponse, CVListResponse
from services.cv_analyzer import CVAnalyzer
from services.file_processor import FileProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CV Analyzer API",
    description="API for uploading and analyzing CVs using OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cv_analyzer = CVAnalyzer()
file_processor = FileProcessor()

@app.get("/")
async def root():
    return {"message": "CV Analyzer API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/upload-cv", response_model=CVResponse)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a CV file and analyze it using OpenAI
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not supported. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Save file and extract text
        file_path, extracted_text = await file_processor.process_file(file, file_content)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from the file"
            )
        
        # Analyze CV using OpenAI
        logger.info(f"Analyzing CV: {file.filename}")
        analysis_result = await cv_analyzer.analyze_cv(extracted_text)
        
        # Save to database
        cv_record = CV(
            filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            upload_time=datetime.utcnow(),
            summary_pros=analysis_result.get("pros", ""),
            summary_cons=analysis_result.get("cons", "")
        )
        
        db.add(cv_record)
        db.commit()
        db.refresh(cv_record)
        
        logger.info(f"CV uploaded and analyzed successfully: {cv_record.id}")
        
        return CVResponse(
            id=cv_record.id,
            filename=cv_record.filename,
            file_size=cv_record.file_size,
            upload_time=cv_record.upload_time,
            summary_pros=cv_record.summary_pros,
            summary_cons=cv_record.summary_cons
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/cv/{cv_id}", response_model=CVResponse)
async def get_cv(cv_id: int, db: Session = Depends(get_db)):
    """
    Get a specific CV analysis by ID
    """
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    return CVResponse(
        id=cv.id,
        filename=cv.filename,
        file_size=cv.file_size,
        upload_time=cv.upload_time,
        summary_pros=cv.summary_pros,
        summary_cons=cv.summary_cons
    )

@app.get("/cv", response_model=List[CVListResponse])
async def list_cvs(db: Session = Depends(get_db)):
    """
    List all uploaded CVs
    """
    cvs = db.query(CV).order_by(CV.upload_time.desc()).all()
    
    return [
        CVListResponse(
            id=cv.id,
            filename=cv.filename,
            file_size=cv.file_size,
            upload_time=cv.upload_time
        )
        for cv in cvs
    ]

@app.delete("/cv/{cv_id}")
async def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    """
    Delete a CV by ID
    """
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    # Delete the physical file if it exists
    if cv.file_path and os.path.exists(cv.file_path):
        try:
            os.remove(cv.file_path)
            logger.info(f"Deleted file: {cv.file_path}")
        except Exception as e:
            logger.error(f"Error deleting file {cv.file_path}: {str(e)}")
    
    # Delete from database
    db.delete(cv)
    db.commit()
    
    logger.info(f"CV deleted successfully: {cv_id}")
    return {"message": "CV deleted successfully", "id": cv_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

