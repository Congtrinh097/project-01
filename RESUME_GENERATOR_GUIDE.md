# Resume Generator Module

## Overview

This module adds professional resume generation capabilities to the CV Analyzer application. It uses LLaMA3 (locally) or a Mock model to generate well-formatted resumes from plain text input and exports them as PDF files.

## Features

- **Text-to-Resume Generation**: Convert plain text information into professional resumes
- **PDF Export**: Automatically generates downloadable PDF files
- **LLaMA3 Integration**: Uses local LLaMA3 model when available, falls back to Mock mode
- **Database Storage**: Stores generated resumes with metadata
- **Web Interface**: Easy-to-use textarea input with live preview
- **Download Links**: Direct download links for generated PDFs

## Architecture

### Backend Components

#### 1. **Resume Generator Service** (`backend/services/resume_generator.py`)
- Handles resume text generation using LLaMA or Mock model
- Two generation modes:
  - `generate_from_text()`: Plain text input
  - `generate_from_profile()`: Structured JSON profile
- Automatic fallback to Mock mode if LLaMA unavailable

#### 2. **PDF Generator Service** (`backend/services/pdf_generator.py`)
- Converts resume text to formatted PDF
- Uses `reportlab` library for PDF generation
- Smart formatting with different styles for headers, sections, and body text
- Auto-generates unique filenames with timestamps

#### 3. **Database Models** (`backend/models.py`)
- New `Resume` model with fields:
  - `input_text`: Original user input
  - `generated_text`: AI-generated resume text
  - `pdf_path`: Path to PDF file
  - `pdf_filename`: PDF filename
  - `file_size`: Size of PDF file
  - `created_at`: Creation timestamp

#### 4. **API Endpoints** (`backend/main.py`)
- `POST /generate-resume`: Generate resume from text input
- `GET /resumes`: List all generated resumes
- `GET /resumes/{id}`: Get specific resume details
- `GET /download-resume/{id}`: Download PDF file
- `DELETE /resumes/{id}`: Delete resume and PDF file

### Frontend Components

#### 1. **Updated App.jsx**
- New "Generate Resume" tab
- Textarea for input text
- Real-time generation status
- Resume preview panel
- Download button for PDFs
- List of previously generated resumes

#### 2. **API Integration** (`frontend/src/services/api.js`)
- `generateResume()`: Submit text for generation
- `getResumes()`: Fetch resume list
- `downloadResume()`: Get download URL
- `deleteResume()`: Delete resume

## Installation

### Backend Requirements

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Key new dependencies:
- `reportlab==4.0.7` - PDF generation
- `llama-cpp-python==0.2.20` - LLaMA model support (optional)

2. (Optional) Set up LLaMA3 model:
```bash
# Create models directory
mkdir -p ./models

# Download your .gguf model file
# Place it in ./models/llama-3.gguf

# Set environment variable
export MODEL_PATH=./models/llama-3.gguf
```

Or create a `.env` file:
```
MODEL_PATH=./models/llama-3.gguf
```

### Database Migration

The new `Resume` model requires database migration:

```bash
cd backend
# If using Alembic
alembic revision --autogenerate -m "Add resume model"
alembic upgrade head

# Or simply restart the app (FastAPI will auto-create tables)
python main.py
```

## Usage

### Web Interface

1. **Start the application**:
```bash
# Backend
cd backend
python main.py

# Frontend
cd frontend
npm run dev
```

2. **Navigate to "Generate Resume" tab**

3. **Enter your information** in the textarea:
```
Name: John Doe
Title: Software Engineer

Experience:
- Senior Developer at Tech Corp (2020-Present)
  * Led development of microservices architecture
  * Improved system performance by 40%
- Junior Developer at StartUp Inc (2018-2020)
  * Built REST APIs and frontend components

Education:
- B.Sc. Computer Science, University XYZ (2018)

Skills: Python, JavaScript, React, Docker, AWS
```

4. **Click "Generate Resume"**

5. **Download the PDF** using the download button

### API Usage

#### Generate Resume

```bash
curl -X POST http://localhost:8000/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Name: John Doe\nTitle: Software Engineer\n..."
  }'
```

Response:
```json
{
  "id": 1,
  "generated_text": "JOHN DOE\nSoftware Engineer\n...",
  "pdf_filename": "resume_20251011_143022.pdf",
  "download_url": "/download-resume/1",
  "file_size": 15420,
  "created_at": "2025-10-11T14:30:22.123Z"
}
```

#### Download PDF

```bash
curl -O http://localhost:8000/download-resume/1
```

Or open in browser:
```
http://localhost:8000/download-resume/1
```

#### List Resumes

```bash
curl http://localhost:8000/resumes
```

#### Delete Resume

```bash
curl -X DELETE http://localhost:8000/resumes/1
```

## Configuration

### Environment Variables

- `MODEL_PATH`: Path to LLaMA .gguf model file (default: `./models/llama-3.gguf`)
- Can be set via `.env` file or system environment

### Output Directory

PDFs are saved to: `backend/outputs/resumes/`
- Directory is auto-created if it doesn't exist
- Filenames format: `resume_YYYYMMDD_HHMMSS.pdf`

## Mock Mode

If LLaMA is not available, the system automatically falls back to Mock mode:

**Features:**
- Generates professional-looking resumes from templates
- Parses input text for key information
- Provides consistent output for testing
- No external model dependencies

**Activation:**
- Automatic when `llama-cpp-python` is not installed
- Automatic when model file is missing
- Manual by not setting `MODEL_PATH`

## PDF Formatting

The PDF generator applies professional formatting:

- **Title Style**: 18pt, Bold, Centered
- **Section Headers**: 14pt, Bold, Blue-gray color
- **Body Text**: 11pt, Regular, Black
- **Bullet Points**: Proper indentation
- **Spacing**: Optimal spacing between sections
- **Margins**: 0.75 inch on all sides

## API Response Examples

### Successful Generation

```json
{
  "id": 1,
  "generated_text": "JOHN DOE\nSoftware Engineer\n...",
  "pdf_filename": "resume_20251011_143022.pdf",
  "download_url": "/download-resume/1",
  "file_size": 15420,
  "created_at": "2025-10-11T14:30:22.123Z"
}
```

### Error Responses

**Empty input:**
```json
{
  "detail": "Input text cannot be empty"
}
```

**Generation failure:**
```json
{
  "detail": "Failed to generate resume text"
}
```

**PDF generation failure:**
```json
{
  "detail": "Failed to generate PDF file"
}
```

## Troubleshooting

### LLaMA Not Loading

**Problem:** Model fails to load

**Solutions:**
1. Check model file exists: `ls -la ./models/`
2. Verify MODEL_PATH environment variable
3. Ensure `llama-cpp-python` is installed: `pip list | grep llama`
4. Check model file format (must be .gguf)
5. System will automatically fall back to Mock mode

### PDF Generation Errors

**Problem:** PDF generation fails

**Solutions:**
1. Ensure `reportlab` is installed: `pip list | grep reportlab`
2. Check write permissions on `outputs/resumes/` directory
3. Verify disk space availability
4. Check logs for specific error messages

### Download Link Not Working

**Problem:** Download link returns 404

**Solutions:**
1. Check if PDF file exists in `outputs/resumes/`
2. Verify resume ID is correct
3. Check backend logs for file path issues
4. Ensure FileResponse is properly configured

## Development

### Adding New Features

**Custom PDF Templates:**
Modify `backend/services/pdf_generator.py`:
- Adjust styles in `text_to_pdf()` method
- Add custom headers/footers
- Change colors and fonts

**Structured Input:**
Use `generate_from_profile()` for JSON input:
```python
profile = {
    "name": "John Doe",
    "title": "Software Engineer",
    "experience": [...],
    "education": [...],
    "skills": [...]
}
resume_text = generator.generate_from_profile(profile)
```

### Testing

**Test Resume Generation:**
```python
from services.resume_generator import ResumeGenerator

generator = ResumeGenerator()
text = "Name: Test User\nTitle: Developer"
resume = generator.generate_from_text(text)
print(resume)
```

**Test PDF Generation:**
```python
from services.pdf_generator import PDFGenerator

pdf_gen = PDFGenerator()
pdf_path = pdf_gen.text_to_pdf("Sample resume text")
print(f"PDF saved to: {pdf_path}")
```

## File Structure

```
backend/
├── services/
│   ├── resume_generator.py  # Resume text generation
│   ├── pdf_generator.py      # PDF conversion
│   ├── cv_analyzer.py         # Existing CV analysis
│   └── file_processor.py      # Existing file processing
├── models.py                  # Database models (+ Resume)
├── schemas.py                 # Pydantic schemas (+ Resume schemas)
├── main.py                    # API endpoints (+ Resume endpoints)
├── requirements.txt           # Dependencies (+ reportlab, llama-cpp-python)
└── outputs/
    └── resumes/               # Generated PDF files

frontend/
├── src/
│   ├── App.jsx                # Main app (+ GenerateResumeTab)
│   └── services/
│       └── api.js             # API calls (+ resume endpoints)
```

## Performance

- **Mock Mode**: ~100-500ms per resume
- **LLaMA Mode**: ~2-10 seconds (depends on model size and hardware)
- **PDF Generation**: ~200-500ms per file
- **Database Operations**: ~10-50ms

## Security Considerations

1. **Input Validation**: Input text is validated before processing
2. **File Permissions**: PDF files are stored with appropriate permissions
3. **Path Traversal**: File paths are sanitized
4. **Rate Limiting**: Consider adding rate limiting for production
5. **Authentication**: Add authentication for production use

## Future Enhancements

- [ ] Multiple PDF templates/themes
- [ ] Upload CV and enhance/rewrite it
- [ ] Support for multiple languages
- [ ] Real-time preview as you type
- [ ] Email delivery of generated resumes
- [ ] Resume templates library
- [ ] ATS (Applicant Tracking System) optimization scoring
- [ ] Export to DOCX format
- [ ] Batch resume generation

## Credits

Based on the resume generation code using LLaMA3 locally. Integrated into the CV Analyzer application with PDF export functionality.

## License

Same as the parent application.

