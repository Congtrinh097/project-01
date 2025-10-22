# Job Recommendation Feature

## Overview

The Job Recommendation feature uses AI-powered semantic search to match candidates with the most suitable job opportunities. It leverages OpenAI embeddings stored in the PostgreSQL database to find jobs that best match a user's skills, experience, and preferences.

## Features

### 1. **Text-Based Job Search**

- Enter your skills, experience, and job preferences as natural language text
- AI analyzes the query and finds matching jobs using semantic similarity
- Supports multiple languages (English, Vietnamese, etc.)

### 2. **CV-Based Job Search**

- Upload your CV (PDF or DOCX format)
- Automatically extracts text from the CV
- Finds jobs that match your profile without manual input
- Supports the same file formats as CV upload (PDF, DOCX)

### 3. **AI-Powered Recommendations**

- Get intelligent summaries of why jobs match your profile
- Personalized recommendations on which positions to apply for first
- Suggestions for skill gaps and development areas
- Language-aware responses (matches your input language)

### 4. **Comprehensive Job Details**

- View position title, company, and location
- See required experience and education
- Browse technical and soft skills needed
- Review benefits and company culture ("Why Join")
- Direct links to apply for positions

## Technical Implementation

### Backend Components

#### 1. **Job Recommender Service** (`backend/services/job_recommender.py`)

Key methods:

- `generate_embedding(text)`: Creates 1536-dimension vector embeddings using OpenAI's `text-embedding-3-small` model
- `find_similar_jobs(embedding, db, limit)`: Performs semantic search using PostgreSQL pgvector cosine similarity
- `generate_ai_recommendation(query, jobs)`: Creates personalized AI summaries using GPT-4o-mini
- `search_and_recommend(query, db, limit)`: Complete workflow from query to recommendations

#### 2. **API Endpoints** (`backend/main.py`)

**POST /job/recommend**

- Request: `{ "query": "text", "limit": 5 }`
- Response: `{ "query": "...", "results": [...], "ai_recommendation": "..." }`
- Used for text-based job searches

**POST /job/recommend-from-cv**

- Request: Multipart form with file upload and limit parameter
- Response: Same as /job/recommend
- Extracts CV text and performs job search

#### 3. **Database Schema** (`backend/models.py`)

Uses the existing `Job` model with `summary_embedding` field:

- Stores 1536-dimensional vectors in PostgreSQL with pgvector
- Enables fast cosine similarity searches
- Automatically populated during job extraction

### Frontend Components

#### 1. **JobRecommendTab Component** (`frontend/src/components/JobRecommendTab.jsx`)

Features:

- Dual input modes: Text query or CV upload
- Configurable result limits (3, 5, 10, 20)
- Real-time loading states
- Error handling with helpful messages
- Responsive design for mobile and desktop

#### 2. **API Integration** (`frontend/src/services/api.js`)

Functions:

- `recommendJobs(query, limit)`: Text-based search
- `recommendJobsFromCV(file, limit)`: CV-based search

#### 3. **Main App Integration** (`frontend/src/App.jsx`)

- Added "Recommend Jobs" navigation item
- State management for job recommendations
- Mutation hooks for API calls
- Error handling and loading states

## Usage Guide

### For Candidates (Text Search)

1. Navigate to the "Recommend Jobs" tab
2. Select "Text Query" mode
3. Enter your skills and preferences, for example:
   ```
   I'm a senior software engineer with 5+ years of Python and React experience.
   Looking for remote positions with good work-life balance and competitive salary.
   ```
4. Select the number of results (3-20)
5. Click "Find Jobs"
6. Review AI recommendations and job matches
7. Click "Apply Now" on jobs that interest you

### For Candidates (CV Upload)

1. Navigate to the "Recommend Jobs" tab
2. Select "Upload CV" mode
3. Click to upload your CV (PDF or DOCX)
4. Select the number of results
5. Click "Find Matching Jobs"
6. Review personalized recommendations
7. Apply directly through the provided links

### For Recruiters (Adding Jobs)

Jobs must be added to the database first before recommendations can work:

1. Go to the "Jobs" tab
2. Use the job extraction feature to add jobs from URLs
3. Jobs are automatically processed with embeddings
4. Jobs become searchable immediately after extraction

## API Request Examples

### Text-Based Search

```bash
curl -X POST http://localhost:8000/job/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer with FastAPI experience",
    "limit": 5
  }'
```

### CV-Based Search

```bash
curl -X POST http://localhost:8000/job/recommend-from-cv \
  -F "file=@my_cv.pdf" \
  -F "limit=5"
```

## Response Format

```json
{
  "query": "Python developer with FastAPI...",
  "results": [
    {
      "id": 1,
      "position": "Senior Python Developer",
      "company": "Tech Corp",
      "job_link": "https://example.com/job/123",
      "location": "Remote",
      "working_type": "Full-time",
      "experience": "5+ years",
      "education": "Bachelor's degree",
      "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
      "soft_skills": ["Communication", "Teamwork"],
      "benefits": ["Health Insurance", "Remote Work"],
      "tags": ["backend", "python", "api"],
      "summary": "We're looking for an experienced Python developer...",
      "similarity_score": 0.8543,
      "posted": "2025-10-20T10:00:00",
      "created_at": "2025-10-21T08:30:00"
    }
  ],
  "ai_recommendation": "Based on your profile, here are my recommendations:\n\n1. **Senior Python Developer at Tech Corp** (85.4% match)..."
}
```

## Key Features & Algorithms

### Semantic Search

- Uses OpenAI's `text-embedding-3-small` model (1536 dimensions)
- Cosine similarity for matching: `similarity = 1 - (embedding1 <=> embedding2)`
- Results sorted by highest similarity first
- Minimum 30% similarity threshold for results

### AI Recommendations

- Analyzes top matching jobs
- Provides personalized insights
- Language-aware responses
- Highlights skill gaps and development opportunities

### Smart Filtering

- Automatically filters out low-quality matches (<30% similarity)
- Generates helpful messages when no matches found
- Suggests how to improve search queries

## Configuration

### Environment Variables

The feature uses the same OpenAI configuration as other services:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBED_API_KEY=your_embedding_api_key  # Optional, falls back to OPENAI_API_KEY
OPENAI_BASE_URL=https://api.openai.com/v1    # Optional, custom endpoint
```

### File Upload Limits

Uses the same settings as CV upload:

- Maximum file size: 10 MB (configurable in `config.py`)
- Allowed formats: PDF, DOCX
- Minimum text length: 50 characters

## Performance Considerations

### Database Indexing

- pgvector creates HNSW or IVFFlat indexes for fast similarity search
- Typical search time: <100ms for thousands of jobs
- Embedding generation: ~100ms per query

### Caching Recommendations

- Embeddings are pre-computed during job extraction
- No embedding regeneration needed for searches
- AI summaries are generated fresh each time (can be cached if needed)

## Error Handling

### Common Errors

1. **No jobs in database**

   - Message: "No matching jobs found in the database"
   - Solution: Add jobs via the Jobs tab first

2. **Low similarity (<30%)**

   - Message: Personalized suggestions to improve search
   - Solution: Broaden search criteria or use different keywords

3. **CV text extraction failed**

   - Message: "Could not extract sufficient text from the CV"
   - Solution: Ensure CV has readable text (not scanned images)

4. **File size too large**
   - Message: "File too large. Maximum size: 10MB"
   - Solution: Compress or reduce CV file size

## Future Enhancements

Potential improvements for the feature:

1. **Advanced Filters**: Add filters for location, salary range, experience level
2. **Save Searches**: Allow users to save and reuse search queries
3. **Job Alerts**: Email notifications for new matching jobs
4. **Application Tracking**: Track which jobs a user has applied to
5. **Batch Processing**: Recommend jobs for multiple CVs at once
6. **Custom Weights**: Let users prioritize certain criteria (salary vs. culture vs. skills)
7. **Interview Prep**: Link to chatbot for interview preparation for matched jobs

## Troubleshooting

### Jobs not appearing in results

1. Check that jobs have `summary_embedding` populated:

   ```sql
   SELECT COUNT(*) FROM jobs WHERE summary_embedding IS NOT NULL;
   ```

2. Verify OpenAI API credentials are correct

3. Check that job summaries are not empty:
   ```sql
   SELECT COUNT(*) FROM jobs WHERE summary IS NOT NULL AND summary != '';
   ```

### Similarity scores always low

1. Ensure embeddings are using the same model (`text-embedding-3-small`)
2. Check that query text is substantial (>50 characters recommended)
3. Verify job summaries contain relevant information

### Frontend not showing results

1. Check browser console for API errors
2. Verify API endpoint URLs in `frontend/src/services/api.js`
3. Ensure CORS is properly configured in backend
4. Check network tab for failed requests

## Integration with Existing Features

### Works With:

- **Jobs Tab**: Jobs added via extraction automatically get embeddings
- **CV Upload**: Can use existing uploaded CVs for recommendations
- **Chatbot**: Can discuss job opportunities and prepare for interviews

### Complements:

- **CV Recommendation**: Reverse matching (find candidates for jobs)
- **Resume Generation**: Create targeted resumes for recommended jobs

## Security Considerations

1. **File Upload Validation**: Only PDF and DOCX files accepted
2. **Size Limits**: 10MB maximum to prevent abuse
3. **Text Extraction**: Sanitized to prevent injection attacks
4. **API Rate Limiting**: Consider adding rate limits for production
5. **CORS**: Configured to allow only trusted frontend origins

## Conclusion

The Job Recommendation feature provides an intelligent, AI-powered way to match candidates with job opportunities. By leveraging semantic search and personalized AI recommendations, it helps users find the best career opportunities efficiently and effectively.

For questions or issues, please open an issue on the GitHub repository.
