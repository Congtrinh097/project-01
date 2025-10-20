from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import logging
from datetime import datetime

from database import get_db, engine
from models import Base, CV, Resume
from schemas import CVResponse, CVListResponse, ResumeGenerateRequest, ResumeResponse, ResumeListResponse, ChatRequest, ChatResponse, CVRecommendRequest, CVRecommendResponse
from services.cv_analyzer import CVAnalyzer
from services.file_processor import FileProcessor
from services.resume_generator import ResumeGenerator
from services.pdf_generator import PDFGenerator
from services.chatbot import InterviewChatbot
from services.cv_recommender import CVRecommender
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

# Configure CORS origins
cors_origins = ["http://localhost:3000", "http://frontend:3000"]

# Add frontend URL from environment if available
if settings.FRONTEND_URL and settings.FRONTEND_URL != "*":
    cors_origins.append(settings.FRONTEND_URL)
    logger.info(f"Added FRONTEND_URL to CORS origins: {settings.FRONTEND_URL}")

# For production, allow all origins if FRONTEND_URL is "*"
if settings.FRONTEND_URL == "*":
    cors_origins = ["*"]
    logger.warning("CORS configured to allow all origins (*)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
cv_analyzer = CVAnalyzer()
file_processor = FileProcessor()
resume_generator = ResumeGenerator()
pdf_generator = PDFGenerator()
chatbot = InterviewChatbot()
cv_recommender = CVRecommender()

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
        
        # Generate embedding for the CV text
        logger.info("Generating embedding for CV...")
        try:
            embedding = cv_recommender.generate_embedding(extracted_text)
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {str(e)}")
            embedding = None
        
        # Save to database
        cv_record = CV(
            filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            upload_time=datetime.utcnow(),
            summary_pros=analysis_result.get("pros", ""),
            summary_cons=analysis_result.get("cons", ""),
            extracted_text=extracted_text,
            embedding=embedding
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

@app.get("/download-cv/{cv_id}")
async def download_cv(cv_id: int, db: Session = Depends(get_db)):
    """
    Download the original CV file
    """
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    if not cv.file_path or not os.path.exists(cv.file_path):
        logger.error(f"CV file not found: {cv.file_path}")
        raise HTTPException(status_code=404, detail="CV file not found")
    
    # Determine media type based on file extension
    file_extension = cv.filename.split('.')[-1].lower()
    media_type_map = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    media_type = media_type_map.get(file_extension, 'application/octet-stream')
    
    return FileResponse(
        path=cv.file_path,
        media_type=media_type,
        filename=cv.filename
    )

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


# ============================================================================
# CV RECOMMENDATION ENDPOINTS
# ============================================================================

@app.post("/cv/recommend", response_model=CVRecommendResponse)
async def recommend_cvs(
    request: CVRecommendRequest,
    db: Session = Depends(get_db)
):
    """
    Semantic search for CVs based on a natural language query.
    Uses vector embeddings and AI to find and recommend the most relevant candidates.
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Validate limit
        limit = min(max(1, request.limit), 20)  # Between 1 and 20
        
        # Perform search and generate recommendation
        logger.info(f"Processing recommendation request: {request.query[:100]}")
        result = cv_recommender.search_and_recommend(
            query=request.query,
            db=db,
            limit=limit
        )
        
        return CVRecommendResponse(
            query=result["query"],
            results=result["results"],
            ai_recommendation=result["ai_recommendation"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in CV recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# RESUME GENERATION ENDPOINTS
# ============================================================================

@app.post("/generate-resume", response_model=ResumeResponse)
async def generate_resume(
    request: ResumeGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a professional resume from input text and return PDF download link
    """
    try:
        if not request.input_text or not request.input_text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty")
        
        # Generate resume text using LLaMA or Mock model
        logger.info("Generating resume text...")
        resume_text = resume_generator.generate_from_text(
            text=request.input_text,
            max_tokens=1000,
            temperature=0.2
        )
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=500,
                detail="Failed to generate resume text"
            )
        
        # Generate PDF from resume text
        logger.info("Generating PDF...")
        pdf_path = pdf_generator.text_to_pdf(resume_text)
        
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF file"
            )
        
        # Get file size
        file_size = os.path.getsize(pdf_path)
        pdf_filename = os.path.basename(pdf_path)
        
        # Save to database
        resume_record = Resume(
            input_text=request.input_text,
            generated_text=resume_text,
            pdf_path=pdf_path,
            pdf_filename=pdf_filename,
            file_size=file_size,
            created_at=datetime.utcnow()
        )
        
        db.add(resume_record)
        db.commit()
        db.refresh(resume_record)
        
        logger.info(f"Resume generated successfully: {resume_record.id}")
        
        # Create download URL
        download_url = f"/download-resume/{resume_record.id}"
        
        return ResumeResponse(
            id=resume_record.id,
            generated_text=resume_record.generated_text,
            pdf_filename=resume_record.pdf_filename,
            download_url=download_url,
            file_size=resume_record.file_size,
            created_at=resume_record.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/resumes", response_model=List[ResumeListResponse])
async def list_resumes(db: Session = Depends(get_db)):
    """
    List all generated resumes
    """
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    
    return [
        ResumeListResponse(
            id=resume.id,
            pdf_filename=resume.pdf_filename,
            file_size=resume.file_size,
            created_at=resume.created_at
        )
        for resume in resumes
    ]


@app.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Get a specific resume by ID
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    download_url = f"/download-resume/{resume.id}"
    
    return ResumeResponse(
        id=resume.id,
        generated_text=resume.generated_text,
        pdf_filename=resume.pdf_filename,
        download_url=download_url,
        file_size=resume.file_size,
        created_at=resume.created_at
    )


@app.get("/download-resume/{resume_id}")
async def download_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Download the PDF file for a generated resume
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not os.path.exists(resume.pdf_path):
        logger.error(f"PDF file not found: {resume.pdf_path}")
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        path=resume.pdf_path,
        media_type='application/pdf',
        filename=resume.pdf_filename
    )


@app.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Delete a resume by ID
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete the physical PDF file if it exists
    if resume.pdf_path and os.path.exists(resume.pdf_path):
        try:
            os.remove(resume.pdf_path)
            logger.info(f"Deleted PDF file: {resume.pdf_path}")
        except Exception as e:
            logger.error(f"Error deleting PDF file {resume.pdf_path}: {str(e)}")
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    logger.info(f"Resume deleted successfully: {resume_id}")
    return {"message": "Resume deleted successfully", "id": resume_id}


# ============================================================================
# CHATBOT ENDPOINTS
# ============================================================================

@app.post("/chatbot", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the interview practice chatbot and get a response
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Convert conversation history to the format expected by the chatbot
        conversation_history = []
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Get response from chatbot
        logger.info(f"Processing chat message: {request.message[:50]}...")
        response_text = chatbot.get_response(
            user_input=request.message,
            conversation_history=conversation_history
        )
        
        return ChatResponse(
            response=response_text,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chatbot endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/chatbot/health")
async def chatbot_health_check():
    """
    Check if the chatbot service is properly configured
    """
    is_configured = chatbot.client is not None
    return {
        "status": "configured" if is_configured else "not_configured",
        "message": "Chatbot is ready" if is_configured else "OpenAI API key not configured",
        "model": chatbot.model_name if is_configured else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

