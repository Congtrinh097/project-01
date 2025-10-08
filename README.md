# CV Analyzer - Full Stack Application

A full-stack web application that allows users to upload their CVs and receive AI-powered analysis using OpenAI's GPT-4o-mini model. The application extracts strengths and areas for improvement from uploaded CVs.

## Features

- **CV Upload**: Upload PDF or DOCX files up to 10MB
- **AI Analysis**: Uses OpenAI GPT-4o-mini to analyze CV content
- **Text Extraction**: Automatically extracts text from PDF and DOCX files
- **Database Storage**: Stores CV metadata and analysis results in PostgreSQL
- **Modern UI**: Clean, responsive interface built with React and TailwindCSS
- **Real-time Progress**: Shows upload and analysis progress
- **History Management**: View previously uploaded CVs and their analyses

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **OpenAI API**: AI-powered CV analysis
- **pdfplumber**: PDF text extraction
- **python-docx**: DOCX text extraction

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **Axios**: HTTP client for API calls
- **Lucide React**: Modern icon library

### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration
- **PostgreSQL**: Database service

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cv-analyzer
   ```

2. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Upload CV
```http
POST /upload-cv
Content-Type: multipart/form-data

Body: file (PDF or DOCX)
```

### Get CV Analysis
```http
GET /cv/{id}
```

### List All CVs
```http
GET /cv
```

### Health Check
```http
GET /health
```

## Project Structure

```
cv-analyzer/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── services/
│   │   ├── cv_analyzer.py      # OpenAI integration
│   │   └── file_processor.py   # File processing
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── main.jsx            # React entry point
│   │   ├── services/
│   │   │   └── api.js          # API client
│   │   └── index.css           # Global styles
│   ├── package.json            # Node dependencies
│   └── Dockerfile              # Frontend container
├── docker-compose.yml          # Service orchestration
├── env.example                 # Environment template
└── README.md                   # This file
```

## Database Schema

### CVs Table
- `id`: Primary key (integer)
- `filename`: Original filename (string)
- `file_path`: Local file path (string)
- `file_size`: File size in bytes (integer)
- `upload_time`: Upload timestamp (datetime)
- `summary_pros`: AI analysis - strengths (text)
- `summary_cons`: AI analysis - areas for improvement (text)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/cv_analyzer` |
| `UPLOAD_DIR` | Directory for file storage | `/tmp/uploads` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `10485760` (10MB) |
| `ALLOWED_EXTENSIONS` | Allowed file extensions | `pdf,docx` |

### File Upload Limits
- Maximum file size: 10MB
- Supported formats: PDF, DOCX
- Files are stored temporarily in `/tmp/uploads/`

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migration
The application automatically creates database tables on startup. For production, consider using Alembic for proper migrations.

## Production Considerations

1. **Security**: Add authentication and authorization
2. **File Storage**: Use cloud storage (S3, GCS) instead of local files
3. **Database**: Use managed PostgreSQL service
4. **Monitoring**: Add logging and monitoring
5. **Rate Limiting**: Implement API rate limiting
6. **SSL**: Use HTTPS in production
7. **Environment**: Use proper environment management

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is valid and has sufficient credits
   - Check the `.env` file has the correct key

2. **File Upload Fails**
   - Check file size (max 10MB)
   - Ensure file is PDF or DOCX format
   - Verify upload directory permissions

3. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`

4. **Frontend Can't Connect to Backend**
   - Verify both services are running
   - Check CORS configuration
   - Ensure correct API URL in frontend

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

