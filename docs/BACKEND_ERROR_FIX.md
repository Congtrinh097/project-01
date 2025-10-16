# Backend Error - Fixed! ✅

## 🐛 Issues Found and Fixed

### 1. Missing Environment Variable in docker-compose.yml
**Problem:** The new `OPENAI_EMBED_API_KEY` wasn't passed to the backend container.

**Fix:** Added to docker-compose.yml:
```yaml
- OPENAI_EMBED_API_KEY=${OPENAI_EMBED_API_KEY:-}
```

### 2. PostgreSQL Missing pgvector Extension
**Problem:** Standard PostgreSQL image doesn't include pgvector extension.

**Fix:** Changed to pgvector-enabled image:
```yaml
postgres:
  image: pgvector/pgvector:pg15  # Was: postgres:15
```

### 3. Database Migration Not Running Automatically
**Problem:** Migrations needed to be run manually.

**Fix:** 
- Added migrations volume mount to automatically run SQL scripts on first startup
- Created `000_init_pgvector.sql` to enable extension
- Updated `001_add_embedding_support.sql` to add columns and index

---

## 🚀 How to Restart Services

### Step 1: Stop Current Containers
```bash
docker-compose down
```

### Step 2: Remove Old Database Volume (IMPORTANT!)
```bash
# This removes the old database without pgvector
docker volume rm project-01_postgres_data

# Or use:
docker-compose down -v
```

⚠️ **Warning:** This will delete all existing CV data. If you have important data, back it up first!

### Step 3: Start Services Fresh
```bash
docker-compose up --build
```

This will:
1. Pull the pgvector-enabled PostgreSQL image
2. Create a new database with pgvector extension
3. Automatically run migration scripts
4. Start backend and frontend

### Step 4: Verify Everything Works
```bash
# Check logs
docker-compose logs backend

# You should see:
# - "Application startup complete"
# - No errors about pgvector or embedding
```

---

## 🔍 Verify Database Setup

Once running, check if pgvector is properly installed:

```bash
# Connect to database
docker exec -it project-01-postgres-1 psql -U postgres -d cv_analyzer

# In psql, run:
\dx  # Should show 'vector' extension

# Check table structure:
\d cvs  # Should show 'embedding' and 'extracted_text' columns

# Exit:
\q
```

---

## 📝 Your .env File Should Have

Make sure your `.env` file in the project root contains:

```env
# Required
OPENAI_API_KEY=your_actual_api_key_here

# Optional (falls back to OPENAI_API_KEY if not set)
OPENAI_EMBED_API_KEY=your_embedding_key_here

# Optional with defaults
OPENAI_BASE_URL=https://aiportalapi.stu-platform.live/jpe
OPENAI_MODEL=gpt-4o-mini
```

---

## ✅ After Restart - Test the Feature

1. **Open the app:** http://localhost:3000

2. **Upload a CV:**
   - Go to "Upload CV" tab
   - Upload a PDF or DOCX file
   - Check backend logs for "Generating embedding for CV..."

3. **Test Recommendation:**
   - Go to "Recommend" tab
   - Enter: `"Looking for a software engineer with Python experience"`
   - Click "Find Candidates"
   - Should return results in 2-5 seconds

---

## 🐛 If You Still Get Errors

### Error: "could not load library pgvector"
**Solution:** Make sure you're using the pgvector image:
```bash
docker-compose down
docker pull pgvector/pgvector:pg15
docker-compose up --build
```

### Error: "relation cvs does not exist"
**Solution:** Database tables haven't been created. Check if backend is creating them:
```bash
docker-compose logs backend | grep "CREATE TABLE"
```

### Error: "OpenAI API key is required"
**Solution:** Check your `.env` file exists and has `OPENAI_API_KEY` set:
```bash
cat .env | grep OPENAI_API_KEY
```

### Error: "column embedding does not exist"
**Solution:** Migration didn't run. Manually apply it:
```bash
docker exec -i project-01-postgres-1 psql -U postgres -d cv_analyzer < backend/migrations/001_add_embedding_support.sql
```

---

## 📊 Expected Startup Sequence

```
1. postgres: Starting... ✓
2. postgres: Running migrations... ✓
   - 000_init_pgvector.sql (enables extension)
   - 001_add_embedding_support.sql (adds columns)
3. backend: Connecting to database... ✓
4. backend: Creating tables (if not exist)... ✓
5. backend: Initializing services... ✓
6. backend: Application startup complete ✓
7. frontend: Starting dev server... ✓
8. frontend: Local: http://localhost:3000 ✓
```

---

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Backend starts without errors
- ✅ Frontend loads at http://localhost:3000
- ✅ "Recommend" tab is visible in navigation
- ✅ Can upload CVs successfully
- ✅ Backend logs show "Generating embedding for CV..."
- ✅ Can search and get recommendations

---

## 💡 Pro Tips

1. **Check logs in real-time:**
   ```bash
   docker-compose logs -f backend
   ```

2. **Restart just backend:**
   ```bash
   docker-compose restart backend
   ```

3. **Clean everything and start fresh:**
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

---

**The backend error should now be fixed! 🎉**

Run `docker-compose down -v && docker-compose up --build` to start fresh.

