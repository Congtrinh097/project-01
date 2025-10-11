"""
pdf_generator.py

Service for converting resume text to PDF format.
Uses reportlab for PDF generation with proper formatting.

Author: AI Assistant
Date: 2025-10-11
"""

import os
import logging
from typing import Optional
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.pdfgen import canvas
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Generate PDF documents from resume text.
    """

    def __init__(self, output_dir: str = "./outputs/resumes"):
        """
        Initialize PDF generator.
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

        if not _REPORTLAB_AVAILABLE:
            logger.warning("reportlab not installed. PDF generation will be limited.")

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")

    def generate_filename(self, prefix: str = "resume") -> str:
        """
        Generate a unique filename for the PDF.
        
        Args:
            prefix: Prefix for the filename
            
        Returns:
            Full path to the PDF file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.pdf"
        return os.path.join(self.output_dir, filename)

    def text_to_pdf(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Convert plain text resume to PDF with formatting.
        
        Args:
            text: Resume text content
            output_path: Optional specific output path. If None, auto-generates.
            
        Returns:
            Path to the generated PDF file
        """
        if not _REPORTLAB_AVAILABLE:
            raise RuntimeError(
                "reportlab is not installed. Install with: pip install reportlab"
            )

        if output_path is None:
            output_path = self.generate_filename()

        # Create the PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        # Container for the 'Flowable' objects
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#1a1a1a',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#2c3e50',
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor='#333333',
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # Parse the text and apply formatting
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                elements.append(Spacer(1, 0.1 * inch))
                continue
            
            # Escape special characters for reportlab
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Detect title (all caps, or first line)
            if line.isupper() and len(line) < 100:
                para = Paragraph(line, title_style)
                elements.append(para)
            # Detect section headers (all caps or ends with colon, or has dashes/equals)
            elif ('=' * 5 in line or '-' * 5 in line):
                elements.append(Spacer(1, 0.05 * inch))
                continue
            elif line.isupper() or (line.endswith(':') and len(line) < 50):
                para = Paragraph(line.rstrip(':'), heading_style)
                elements.append(para)
            # Bullet points
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Add indent for bullets
                bullet_text = line[1:].strip() if line[0] in ['•', '-', '*'] else line
                para = Paragraph(f"&bull; {bullet_text}", body_style)
                elements.append(para)
            # Regular text
            else:
                para = Paragraph(line, body_style)
                elements.append(para)

        # Build PDF
        try:
            doc.build(elements)
            logger.info(f"Successfully generated PDF: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise RuntimeError(f"Failed to generate PDF: {e}")

    def simple_text_to_pdf(self, text: str, output_path: Optional[str] = None) -> str:
        """
        Simple fallback method to create PDF using canvas (no formatting).
        
        Args:
            text: Resume text content
            output_path: Optional specific output path
            
        Returns:
            Path to the generated PDF file
        """
        if not _REPORTLAB_AVAILABLE:
            raise RuntimeError(
                "reportlab is not installed. Install with: pip install reportlab"
            )

        if output_path is None:
            output_path = self.generate_filename()

        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        # Set up text object
        text_object = c.beginText(0.75 * inch, height - 0.75 * inch)
        text_object.setFont("Helvetica", 11)

        # Split text into lines and add to canvas
        lines = text.split('\n')
        for line in lines:
            text_object.textLine(line)

        c.drawText(text_object)
        c.save()

        logger.info(f"Successfully generated simple PDF: {output_path}")
        return output_path

