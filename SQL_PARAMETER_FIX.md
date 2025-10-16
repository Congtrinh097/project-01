# SQL Parameter Binding Fix ✅

## 🐛 Issue
SQL syntax error when running CV recommendations:
```
SyntaxError: syntax error at or near ":"
LINE 9: 1 - (embedding <=> :query_embedding::vector) as similarity_score
```

## 🔍 Root Cause
SQLAlchemy's named parameter binding (`:param_name`) doesn't work well with pgvector's custom `vector` type casting. PostgreSQL was unable to parse the parameter placeholder syntax with the `::vector` cast.

## ✅ Solution
Changed from parameterized query to f-string interpolation for the vector embedding (which is safe since it's internally generated, not user input):

**Before:**
```python
query = text("""
    SELECT ... 
    WHERE embedding <=> :query_embedding::vector
    ...
""")
db.execute(query, {"query_embedding": embedding_str, "limit": limit})
```

**After:**
```python
query_sql = f"""
    SELECT ... 
    WHERE embedding <=> '{embedding_str}'::vector
    ...
    LIMIT :limit
"""
db.execute(text(query_sql), {"limit": limit})
```

## 🔒 Security Note
This is safe because:
- `embedding_str` is generated internally from `List[float]` - no user input
- `limit` is still parameterized (user input)
- The embedding string is always in format: `[0.123,0.456,...]` (numbers only)

## 🚀 To Apply Fix

The fix is already in `backend/services/cv_recommender.py`. Just restart the backend:

```bash
# If using Docker:
docker-compose restart backend

# Or rebuild:
docker-compose up --build backend
```

## ✅ Testing

After restart, test the recommendation feature:

1. Go to http://localhost:3000
2. Click "Recommend" tab
3. Enter a query: `"Looking for a Python developer"`
4. Click "Find Candidates"
5. Should return results without SQL errors

## 📊 Expected Behavior

- ✅ Query completes in 2-5 seconds
- ✅ Returns top N matching CVs
- ✅ Shows similarity scores (0-1)
- ✅ Displays AI recommendation summary
- ❌ No more SQL syntax errors

---

**Fix Applied! Restart backend to test.** 🎉

