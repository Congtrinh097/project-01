# Job Extraction Feature

## Overview

The Job Extraction feature allows users to extract structured job information from job posting URLs using AI. This feature uses OpenAI's GPT-4o-mini model to analyze job postings and extract key information in a standardized format.

## Features

- **URL-based Extraction**: Extract job information from multiple URLs in a single request
- **Structured Data**: Returns standardized JSON format with all key job details
- **Database Storage**: All extractions are saved to PostgreSQL for future reference
- **RESTful API**: Full CRUD operations for managing job extractions
- **Health Monitoring**: Health check endpoint to verify service configuration

## API Endpoints

### 1. Extract Jobs

**POST** `/extract-jobs`

Extract job information from a list of URLs.

**Request Body:**

```json
{
  "urls": ["https://example.com/job1", "https://example.com/job2"]
}
```

**Response:**

```json
{
  "message": "Jobs extracted and saved successfully",
  "urls": ["https://example.com/job1", "https://example.com/job2"],
  "extracted_data": [
    {
      "position": "Software Engineer",
      "company": "Tech Corp",
      "job_link": "https://example.com/job1",
      "location": "San Francisco, CA",
      "working_type": "Full-time",
      "skills": ["Python", "React", "AWS"],
      "responsibilities": ["Develop web applications", "Code reviews"],
      "requirements": {
        "education": "Bachelor's degree in Computer Science",
        "experience": "3+ years",
        "technical_skills": ["Python", "JavaScript", "SQL"],
        "soft_skills": ["Communication", "Teamwork"]
      },
      "benefits": ["Health insurance", "401k"],
      "company_size": "100-500 employees",
      "why_join": ["Great culture", "Growth opportunities"],
      "posted": "2024-01-15T10:00:00Z",
      "summary": "Exciting opportunity for a software engineer...",
      "tags": ["Python", "React", "AWS", "Full-stack", "Web Development"]
    }
  ],
  "count": 1,
  "saved_job_ids": [1, 2]
}
```

### 2. Health Check

**GET** `/extract-jobs/health`

Check if the job extraction service is properly configured.

**Response:**

```json
{
  "status": "configured",
  "message": "Job extraction is ready",
  "model": "gpt-4o-mini"
}
```

## Individual Jobs Endpoints

### 3. List Jobs

**GET** `/jobs`

List all jobs with optional filtering.

**Query Parameters:**

- `company` (optional): Filter by company name
- `location` (optional): Filter by location
- `working_type` (optional): Filter by working type
- `limit` (optional): Maximum number of results (default: 50, max: 100)

**Response:**

```json
[
  {
    "id": 1,
    "position": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "working_type": "Full-time",
    "tags": ["Python", "React", "AWS"],
    "created_at": "2024-01-15T12:00:00Z"
  }
]
```

### 4. Get Job

**GET** `/jobs/{job_id}`

Get a specific job by ID.

**Response:**

```json
{
  "id": 1,
  "position": "Software Engineer",
  "company": "Tech Corp",
  "job_link": "https://example.com/job1",
  "location": "San Francisco, CA",
  "working_type": "Full-time",
  "skills": ["Python", "React", "AWS"],
  "responsibilities": ["Develop web applications"],
  "education": "Bachelor's degree",
  "experience": "3+ years",
  "technical_skills": ["Python", "JavaScript"],
  "soft_skills": ["Communication"],
  "benefits": ["Health insurance", "401k"],
  "company_size": "100-500 employees",
  "why_join": ["Great culture"],
  "posted": "2024-01-15T10:00:00Z",
  "tags": ["Python", "React", "AWS", "Full-stack"],
  "created_at": "2024-01-15T12:00:00Z"
}
```

### 5. Search Jobs

**GET** `/jobs/search`

Search jobs by position, company, or location.

**Query Parameters:**

- `q` (required): Search query
- `limit` (optional): Maximum number of results (default: 20, max: 50)

**Response:** Same as List Jobs response.

### 6. Delete Job

**DELETE** `/jobs/{job_id}`

Delete a job by ID.

**Response:**

```json
{
  "message": "Job deleted successfully",
  "id": 1
}
```

## Database Schema

### jobs Table

| Column            | Type                     | Description                    |
| ----------------- | ------------------------ | ------------------------------ |
| id                | SERIAL PRIMARY KEY       | Unique identifier              |
| position          | VARCHAR(255)             | Job position/title             |
| company           | VARCHAR(255)             | Company name                   |
| job_link          | VARCHAR(500)             | Original job posting URL       |
| location          | VARCHAR(255)             | Job location                   |
| working_type      | VARCHAR(100)             | Type of work (Full-time, etc.) |
| skills            | JSON                     | Array of required skills       |
| responsibilities  | JSON                     | Array of job responsibilities  |
| education         | VARCHAR(255)             | Education requirements         |
| experience        | VARCHAR(255)             | Experience requirements        |
| technical_skills  | JSON                     | Array of technical skills      |
| soft_skills       | JSON                     | Array of soft skills           |
| benefits          | JSON                     | Array of job benefits          |
| company_size      | VARCHAR(100)             | Company size information       |
| why_join          | JSON                     | Array of reasons to join       |
| posted            | TIMESTAMP WITH TIME ZONE | When the job was posted        |
| summary           | TEXT                     | Job summary/description        |
| tags              | JSON                     | Array of classification tags   |
| summary_embedding | VECTOR(1536)             | OpenAI embedding for summary   |
| created_at        | TIMESTAMP WITH TIME ZONE | When this record was created   |

## Implementation Details

### Service Architecture

The job extraction feature follows the same architectural patterns as other services in the project:

1. **Service Layer** (`services/job_extractor.py`): Contains the business logic for job extraction
2. **Model Layer** (`models.py`): Database model for job extractions
3. **Schema Layer** (`schemas.py`): Pydantic models for request/response validation
4. **API Layer** (`main.py`): FastAPI endpoints

### Key Components

#### JobExtractor Service

- **OpenAI Integration**: Uses GPT-4o-mini for job extraction and text-embedding-3-small for embeddings
- **Prompt Engineering**: Structured prompts for consistent extraction
- **Embedding Generation**: Automatically generates embeddings for job summaries
- **Error Handling**: Comprehensive error handling and logging
- **Configuration**: Health check and configuration validation

#### Database Model

- **JSON Storage**: Uses PostgreSQL JSON columns for flexible data storage
- **Vector Storage**: Uses pgvector for storing embeddings with cosine similarity indexing
- **Indexing**: Optimized queries with proper indexing including vector similarity search
- **Timestamps**: Automatic timestamp tracking

### AI Prompt Structure

The system uses a carefully crafted prompt that:

- Requests structured JSON output with `response_format={"type": "json_object"}`
- Specifies the exact data format required with a "jobs" key containing an array
- Includes guidelines for data extraction
- Handles multilingual content (Vietnamese support)
- Ensures valid JSON format through OpenAI's response format parameter

## Usage Examples

### Python Client Example

```python
import requests

# Extract jobs from URLs
urls = [
    "https://company.com/careers/software-engineer",
    "https://startup.com/jobs/frontend-dev"
]

response = requests.post(
    "http://localhost:8000/extract-jobs",
    json={"urls": urls}
)

if response.status_code == 200:
    result = response.json()
    print(f"Extracted {result['count']} jobs")
    for job in result['extracted_data']:
        print(f"Position: {job['position']} at {job['company']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/extract-jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/job1",
      "https://example.com/job2"
    ]
  }'
```

## Configuration

### Environment Variables

The job extraction service requires the following environment variable:

- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4o-mini access

### Database Migration

Run the migrations to set up the database:

```sql
-- Run the migration files
\i backend/migrations/004_add_jobs_table.sql
\i backend/migrations/006_add_summary_embedding_to_jobs.sql
```

## Error Handling

The service handles various error scenarios:

- **No URLs provided**: Returns 400 Bad Request
- **OpenAI API errors**: Returns 500 Internal Server Error with details
- **Invalid JSON response**: Returns 500 with parsing error details
- **Database errors**: Returns 500 with database error details

## Testing

Use the provided test script to verify the functionality:

```bash
python backend/test_job_extraction.py
```

## Performance Considerations

- **Rate Limiting**: OpenAI API has rate limits; consider implementing retry logic
- **Batch Processing**: Process multiple URLs in a single request for efficiency
- **Caching**: Consider caching results for frequently accessed extractions
- **Database Indexing**: Proper indexing on created_at for list queries

## Security Considerations

- **Input Validation**: All URLs are validated before processing
- **API Key Security**: OpenAI API key is stored securely in environment variables
- **Error Messages**: Sensitive information is not exposed in error responses

## Embedding Features

### Summary Embeddings

The system automatically generates embeddings for job summaries using OpenAI's `text-embedding-3-small` model:

- **Automatic Generation**: Embeddings are created during job extraction
- **Vector Storage**: Stored as 1536-dimensional vectors in PostgreSQL with pgvector
- **Semantic Search**: Enables similarity-based search across job summaries
- **Performance**: Indexed with cosine similarity for fast vector operations
- **API Response**: Summary and embedding fields are stored in database but not included in API responses to reduce payload size

### Embedding Usage

```python
# Embeddings are automatically generated and stored
# They can be used for semantic search queries
# Example: Find jobs similar to a given description
```

### Database Indexing

The system includes optimized indexing for vector operations:

```sql
-- Vector similarity index for fast searches
CREATE INDEX idx_jobs_summary_embedding ON jobs
USING ivfflat (summary_embedding vector_cosine_ops)
WITH (lists = 100);
```

## Future Enhancements

Potential improvements for the job extraction feature:

1. **Semantic Search API**: Add endpoint for similarity-based job search
2. **Web Scraping**: Direct web scraping for better data extraction
3. **Caching**: Redis caching for frequently accessed job data
4. **Batch Processing**: Async processing for large URL lists
5. **Data Validation**: Enhanced validation of extracted job data
6. **Export Features**: Export extracted data to various formats (CSV, Excel)
7. **Advanced Analytics**: Track extraction success rates and patterns
8. **Multi-language Embeddings**: Support for embeddings in different languages
