import os
import uuid
from fastapi import UploadFile
from typing import Tuple
import logging
import pdfplumber
from docx import Document
from config import settings

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        
    async def process_file(self, file: UploadFile, file_content: bytes) -> Tuple[str, str]:
        """
        Process uploaded file and extract text content
        Returns tuple of (file_path, extracted_text)
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Extract text based on file type
            if file_extension == "pdf":
                extracted_text = self._extract_pdf_text(file_path)
            elif file_extension == "docx":
                extracted_text = self._extract_docx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            logger.info(f"File processed successfully: {unique_filename}")
            return file_path, extracted_text
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text from PDF file using pdfplumber
        """
        try:
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_docx_text(self, file_path: str) -> str:
        """
        Extract text from DOCX file using python-docx
        """
        try:
            doc = Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

