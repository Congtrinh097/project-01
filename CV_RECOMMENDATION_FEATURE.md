# CV Recommendation Feature - Implementation Guide

## 📋 Overview

The CV Recommendation feature enables semantic search of CVs using AI-powered vector embeddings. Users can search for candidates using natural language queries, and the system will find the most relevant CVs based on meaning, not just keywords.

---

## 🎯 Features

- **Semantic Search**: Find CVs by meaning using natural language queries
- **Vector Embeddings**: Uses OpenAI's `text-embedding-3-small` model (1536 dimensions)
- **PostgreSQL + pgvector**: Efficient similarity search using cosine distance
- **AI Recommendations**: GPT-powered summaries of top matches
- **Beautiful UI**: Modern, responsive interface with Tailwind CSS

---

## 🏗️ Architecture

### Backend Components

1. **Database Model** (`backend/models.py`)
   - Added `extracted_text` column to store full CV text
   - Added `embedding` vector column (1536 dimensions)

2. **CV Recommender Service** (`backend/services/cv_recommender.py`)
   - `generate_embedding()`: Creates vector embeddings for text
   - `find_similar_cvs()`: Queries database using cosine similarity
   - `generate_ai_recommendation()`: Creates AI-powered summaries
   - `search_and_recommend()`: Complete workflow orchestration

3. **API Endpoint** (`backend/main.py`)
   - `POST /cv/recommend`: Main recommendation endpoint
   - Updated `POST /upload-cv`: Now generates embeddings on upload

4. **Schemas** (`backend/schemas.py`)
   - `CVRecommendRequest`: Input validation
   - `CVRecommendResponse`: Response structure
   - `CVRecommendResult`: Individual result format

### Frontend Components

1. **RecommendTab** (`frontend/src/components/RecommendTab.jsx`)
   - Search form with natural language input
   - Results display with similarity scores
   - AI recommendation summary
   - Beautiful gradient UI with purple theme

2. **App.jsx Updates**
   - New "Recommend" navigation tab with Sparkles icon
   - Mutation hook for API calls
   - State management for results

3. **API Service** (`frontend/src/services/api.js`)
   - `recommendCVs()`: API call function

---

## 🚀 Setup Instructions

### 1. Database Setup

First, enable the pgvector extension in your PostgreSQL database:

```sql
-- Run as superuser
CREATE EXTENSION IF NOT EXISTS vector;
```

Then, run the migration script:

```bash
# Connect to your database
psql -U postgres -d cv_analyzer

# Run the migration
\i backend/migrations/001_add_embedding_support.sql
```

Or manually run:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add new columns to cvs table
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS extracted_text TEXT,
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS cvs_embedding_idx ON cvs 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The new dependency added:
- `pgvector==0.2.4`

### 3. Environment Configuration

Make sure your `.env` file has the OpenAI API key configured:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.live/jpe
```

### 4. Install Frontend Dependencies (if needed)

```bash
cd frontend
npm install
```

### 5. Restart Services

```bash
# Stop existing services
# Then restart with:

# Option 1: Using Docker Compose
docker-compose down
docker-compose up --build

# Option 2: Manual restart
# Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

---

## 📖 Usage Guide

### 1. Upload CVs

First, upload some CVs through the "Upload CV" tab. The system will:
- Extract text from PDF/DOCX files
- Generate embeddings automatically
- Store both text and embeddings in the database

### 2. Search for Candidates

Navigate to the **"Recommend"** tab (sparkles icon ✨)

**Example Queries:**

```
"Looking for a senior software engineer with 5+ years of Python and React experience"

"Need a data scientist with machine learning expertise and PhD in Computer Science"

"Frontend developer experienced in TypeScript, React, and modern web technologies"

"Project manager with Agile certification and healthcare industry experience"

"Full-stack developer with strong communication skills and startup experience"
```

### 3. Review Results

The system will return:
- **AI Recommendation Summary**: Overall assessment of the matches
- **Top Matching CVs**: Ranked by similarity score
  - Similarity percentage (0-100%)
  - CV preview
  - Key strengths
  - Upload date

---

## 🔧 Technical Details

### Vector Embedding Process

1. **Text Extraction**: When a CV is uploaded, text is extracted using `pdfplumber` or `python-docx`
2. **Embedding Generation**: Text is sent to OpenAI's `text-embedding-3-small` model
3. **Storage**: 1536-dimensional vector is stored in PostgreSQL using pgvector

### Similarity Search

```python
# Uses cosine distance operator (<=>)
# Lower distance = higher similarity
SELECT 
    id,
    filename,
    1 - (embedding <=> query_embedding::vector) as similarity_score
FROM cvs
WHERE embedding IS NOT NULL
ORDER BY embedding <=> query_embedding::vector
LIMIT 5;
```

### AI Recommendation

The system uses GPT-4o-mini to analyze the top matches and provide:
- Overview of what was found
- Why candidates match the query
- Key strengths and qualifications
- Recommendation on which candidate(s) to prioritize

---

## 📊 API Reference

### POST /cv/recommend

**Request Body:**
```json
{
  "query": "Looking for a senior software engineer...",
  "limit": 5
}
```

**Response:**
```json
{
  "query": "Looking for a senior software engineer...",
  "results": [
    {
      "id": 1,
      "filename": "john_doe_cv.pdf",
      "similarity_score": 0.8542,
      "text_preview": "Senior Software Engineer with 8 years...",
      "summary_pros": "- Strong Python and React experience...",
      "upload_time": "2025-10-16T10:30:00"
    }
  ],
  "ai_recommendation": "Based on your search query..."
}
```

**Parameters:**
- `query` (required): Natural language search query
- `limit` (optional): Number of results (1-20, default: 5)

**Error Responses:**
- `400`: Empty query or invalid parameters
- `500`: Server error (embedding generation, database, etc.)

---

## 🎨 UI Components

### RecommendTab Features

1. **Search Form**
   - Multi-line textarea for detailed queries
   - Dropdown to select number of results (3, 5, 10, 20)
   - Loading state with spinner
   - Form validation

2. **AI Recommendation Card**
   - Gradient purple/blue background
   - Sparkles icon
   - Formatted text display

3. **Results List**
   - Ranked display with position numbers
   - Similarity percentage badges
   - CV preview snippets
   - Key strengths summary
   - Hover effects

4. **Empty States**
   - No results found message
   - Upload prompt for empty database

---

## 🧪 Testing

### Test the Feature

1. **Upload Test CVs**
   - Upload 5-10 different CVs with varied backgrounds
   - Check that embeddings are generated (check database)

2. **Verify Database**
   ```sql
   SELECT id, filename, 
          LENGTH(extracted_text) as text_length,
          array_length(embedding::float[], 1) as embedding_dim
   FROM cvs
   WHERE embedding IS NOT NULL;
   ```

3. **Test Searches**
   - Try specific queries (e.g., "Python developer")
   - Try broad queries (e.g., "experienced professional")
   - Try queries with no matches
   - Verify similarity scores are reasonable (0.5-0.95 range)

4. **Check Performance**
   - Search should complete in 2-5 seconds
   - Results should be relevant to query
   - AI recommendation should make sense

---

## 🐛 Troubleshooting

### Common Issues

1. **"pgvector extension not found"**
   ```bash
   # Install pgvector on your system first
   # Ubuntu/Debian:
   sudo apt-get install postgresql-15-pgvector
   
   # Then enable in database:
   psql -U postgres -d cv_analyzer -c "CREATE EXTENSION vector;"
   ```

2. **"No matching CVs found" for all queries**
   - Check if CVs have embeddings: `SELECT COUNT(*) FROM cvs WHERE embedding IS NOT NULL;`
   - Re-upload CVs if embeddings are missing
   - Check OpenAI API key is valid

3. **Slow search performance**
   - Verify the index was created: `\d cvs` in psql
   - For large datasets (>1000 CVs), adjust the `lists` parameter in the index

4. **Frontend shows error**
   - Check browser console for details
   - Verify backend is running: `http://localhost:8000/health`
   - Check CORS settings if accessing from different domain

---

## 🔐 Security Considerations

1. **API Key Protection**: Never commit `.env` file with real API keys
2. **Input Validation**: Queries are validated on both frontend and backend
3. **Rate Limiting**: Consider adding rate limits for production
4. **Database Access**: Ensure proper PostgreSQL user permissions

---

## 🚀 Future Enhancements

Potential improvements:

1. **Filters**: Add filters by upload date, file type, etc.
2. **Advanced Search**: Combine semantic search with keyword filters
3. **Candidate Comparison**: Compare multiple CVs side-by-side
4. **Export Results**: Export search results to CSV/PDF
5. **Search History**: Save and replay previous searches
6. **Feedback Loop**: Allow users to mark results as relevant/irrelevant
7. **Multi-language Support**: Handle CVs in different languages
8. **Skills Extraction**: Automatically extract and tag skills from CVs

---

## 📝 Notes

- **Embedding Cost**: Each CV upload costs ~$0.0001 (very cheap)
- **Search Cost**: Each search query costs ~$0.0001
- **Storage**: Each embedding takes ~6KB in database
- **Index Performance**: IVFFlat index is approximate but very fast
- **Similarity Threshold**: Scores above 0.7 are generally good matches

---

## 👥 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the backend logs for detailed error messages
3. Test the API endpoint directly using Postman/curl
4. Verify database schema matches the migration script

---

**Happy Recruiting! 🎉**

