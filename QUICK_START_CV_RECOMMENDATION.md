# Quick Start Guide - CV Recommendation Feature

## 🚀 Get Started in 5 Minutes

Follow these steps to get the CV Recommendation feature up and running:

---

## Step 1: Database Setup (2 minutes)

### Enable pgvector Extension

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# In psql:
\c cv_analyzer
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Run Migration Script

```bash
# From project root
psql -U postgres -d cv_analyzer -f backend/migrations/001_add_embedding_support.sql
```

**Verify it worked:**
```sql
-- Check if columns exist
\d cvs

-- You should see:
-- extracted_text | text
-- embedding      | vector(1536)
```

---

## Step 2: Install Backend Dependencies (1 minute)

```bash
cd backend
pip install pgvector==0.2.4
```

**Or reinstall all dependencies:**
```bash
pip install -r requirements.txt
```

---

## Step 3: Verify Configuration (30 seconds)

Check your `.env` file has:

```env
OPENAI_API_KEY=your_actual_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.live/jpe
DATABASE_URL=postgresql://postgres:password@localhost:5432/cv_analyzer
```

---

## Step 4: Restart Services (1 minute)

### Option A: Docker (Recommended)
```bash
# From project root
docker-compose down
docker-compose up --build
```

### Option B: Manual
```bash
# Terminal 1 - Backend
cd backend
python main.py  # or: uvicorn main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

---

## Step 5: Test the Feature (1 minute)

1. **Open the app**: http://localhost:3000

2. **Upload some CVs**:
   - Click "Upload CV" tab
   - Upload 2-3 PDF or DOCX CVs
   - Wait for analysis to complete
   - **Check backend logs** - you should see "Generating embedding for CV..."

3. **Try the Recommendation**:
   - Click the **"Recommend"** tab (sparkles icon ✨)
   - Enter a query like: `"Looking for a software engineer with Python experience"`
   - Click "Find Candidates"
   - Wait 3-5 seconds for results

4. **Review Results**:
   - You should see AI recommendation summary
   - List of matching CVs with similarity scores
   - The most relevant CVs should have scores > 70%

---

## ✅ Verification Checklist

Check that everything works:

- [ ] pgvector extension installed in PostgreSQL
- [ ] Migration script ran successfully
- [ ] `cvs` table has `extracted_text` and `embedding` columns
- [ ] Backend starts without errors
- [ ] Frontend shows "Recommend" tab in navigation
- [ ] Can upload CVs successfully
- [ ] Backend logs show "Generating embedding for CV..."
- [ ] Can search and get results in Recommend tab
- [ ] AI recommendation appears in results
- [ ] Similarity scores are reasonable (0.5-0.95)

---

## 🐛 Troubleshooting

### Problem: "CREATE EXTENSION vector" fails

**Solution:**
```bash
# Install pgvector system package first
# Ubuntu/Debian:
sudo apt-get install postgresql-15-pgvector

# macOS:
brew install pgvector

# Then retry CREATE EXTENSION
```

### Problem: "No matching CVs found" for every query

**Check:**
```sql
-- How many CVs have embeddings?
SELECT COUNT(*) FROM cvs WHERE embedding IS NOT NULL;
```

**If 0:**
- Re-upload CVs (they'll get embeddings automatically)
- Check backend logs for embedding errors
- Verify OPENAI_API_KEY is valid

### Problem: Backend error "could not import pgvector"

**Solution:**
```bash
pip install pgvector==0.2.4
# Then restart backend
```

### Problem: Search takes > 10 seconds

**Solution:**
```sql
-- Verify index exists
\d cvs

-- If no index, create it:
CREATE INDEX cvs_embedding_idx ON cvs 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Problem: Frontend shows "Recommend" tab but clicking errors

**Check:**
- Backend is running (http://localhost:8000/health)
- Check browser console for error messages
- Verify API_URL is correct in frontend/.env

---

## 🎯 Quick Test Queries

Try these queries to test the feature:

```
"Senior software engineer with 5+ years Python experience"

"Data scientist with machine learning and PhD"

"Frontend developer experienced in React and TypeScript"

"Project manager with agile certification"

"Full-stack developer with strong communication skills"
```

---

## 📊 Expected Results

**Good Results:**
- Search completes in 2-5 seconds
- Similarity scores between 0.5-0.95
- Higher scores for more relevant CVs
- AI recommendation mentions specific matches

**If Results Look Wrong:**
- Scores all very low (< 0.3): Query might be too specific
- Scores all very high (> 0.95): Database might have duplicates
- No variation in scores: Check if embeddings are actually different

---

## 🎉 You're Done!

The CV Recommendation feature is now ready to use. 

**Next steps:**
- Read `CV_RECOMMENDATION_FEATURE.md` for detailed documentation
- Check `IMPLEMENTATION_SUMMARY_CV_RECOMMENDATION.md` for technical details
- Upload more CVs to improve search quality
- Try different types of queries

---

## 💬 Need Help?

1. Check backend logs: `docker-compose logs backend` or console output
2. Check frontend console in browser DevTools
3. Test API directly: `curl -X POST http://localhost:8000/cv/recommend -H "Content-Type: application/json" -d '{"query":"software engineer","limit":5}'`
4. Review the troubleshooting section in `CV_RECOMMENDATION_FEATURE.md`

**Happy searching! 🔍✨**

