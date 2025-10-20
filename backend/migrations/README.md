# Database Migrations Guide

This directory contains SQL migration files for setting up the CV Analyzer database schema.

## 📋 Migration Files

| File                            | Description                    | When to Run                         |
| ------------------------------- | ------------------------------ | ----------------------------------- |
| `000_init_pgvector.sql`         | Enable pgvector extension      | First time setup                    |
| `001_add_embedding_support.sql` | Add embedding columns (legacy) | Upgrading old schema                |
| `002_complete_schema.sql`       | Complete database schema       | **Recommended for new deployments** |
| `quick_setup.sql`               | Quick setup (minimal)          | Fast development setup              |

## 🚀 Quick Setup (Recommended)

### For Supabase (FREE):

1. **Login** to https://supabase.com/dashboard
2. **Select** your project
3. **Go to** SQL Editor
4. **Copy and paste** `002_complete_schema.sql`
5. **Click** "Run"

✅ Done! Your database is ready.

### For Cloud SQL:

```bash
# Connect to Cloud SQL
gcloud sql connect cv-analyzer-db --user=postgres

# Run in psql prompt
\c cv_analyzer
\i backend/migrations/002_complete_schema.sql
\q
```

### For Local PostgreSQL:

```bash
# Connect to local database
psql -U postgres -d cv_analyzer -f backend/migrations/002_complete_schema.sql
```

## 📊 Database Schema

### CVs Table

Stores uploaded CV files and AI analysis results.

```sql
cvs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    summary_pros TEXT,                    -- AI-generated strengths
    summary_cons TEXT,                    -- AI-generated improvements
    extracted_text TEXT,                  -- Full CV text
    embedding vector(1536)                -- For semantic search
)
```

**Indexes**:

- `cvs_embedding_idx` - Vector similarity search (ivfflat)
- `cvs_upload_time_idx` - Query by upload time
- `cvs_filename_idx` - Query by filename

### Resumes Table

Stores AI-generated resumes.

```sql
resumes (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,             -- User input
    generated_text TEXT NOT NULL,         -- AI-generated content
    pdf_path VARCHAR(500) NOT NULL,       -- PDF file path
    pdf_filename VARCHAR(255) NOT NULL,   -- PDF filename
    file_size INTEGER NOT NULL,           -- PDF file size
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
```

**Indexes**:

- `resumes_created_at_idx` - Query by creation time

## 🔄 Migration Order

If running migrations step by step:

```sql
-- 1. Enable pgvector
\i 000_init_pgvector.sql

-- 2. Create complete schema
\i 002_complete_schema.sql
```

## ✅ Verify Setup

After running migrations, verify everything is set up correctly:

```sql
-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- List all tables
\dt

-- Check CVs table structure
\d cvs

-- Check Resumes table structure
\d resumes

-- Check indexes
\di
```

## 🧪 Test Queries

```sql
-- Count CVs
SELECT COUNT(*) FROM cvs;

-- Recent CVs
SELECT id, filename, upload_time FROM cvs ORDER BY upload_time DESC LIMIT 10;

-- Count resumes
SELECT COUNT(*) FROM resumes;

-- Recent resumes
SELECT id, pdf_filename, created_at FROM resumes ORDER BY created_at DESC LIMIT 10;
```

## 🔧 Troubleshooting

### Error: "extension 'vector' does not exist"

**Solution**: Install pgvector extension first.

For Supabase: It's pre-installed, just run `CREATE EXTENSION IF NOT EXISTS vector;`

For Cloud SQL/PostgreSQL:

```bash
# Install pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Error: "relation 'cvs' already exists"

**Solution**: The table already exists. You can either:

- Drop and recreate: `DROP TABLE cvs CASCADE; DROP TABLE resumes CASCADE;` then run migration
- Skip: The migration uses `CREATE TABLE IF NOT EXISTS`, so it's safe to re-run

### Error: Permission denied

**Solution**: Make sure your database user has CREATE privileges:

```sql
GRANT CREATE ON SCHEMA public TO your_user;
```

## 📝 Adding New Migrations

When adding new migrations:

1. **Create** a new file: `003_your_migration_name.sql`
2. **Use** `IF NOT EXISTS` clauses to make it idempotent
3. **Add** comments explaining what and why
4. **Update** this README
5. **Test** on development database first

## 🗑️ Rollback

To rollback/reset the database:

```sql
-- Warning: This will delete all data!
DROP TABLE IF EXISTS cvs CASCADE;
DROP TABLE IF EXISTS resumes CASCADE;
DROP EXTENSION IF EXISTS vector;
```

Then re-run `002_complete_schema.sql` to recreate.

## 📚 Additional Resources

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase SQL Editor](https://supabase.com/docs/guides/database/overview)
- [PostgreSQL CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html)
- [Vector Indexes Guide](https://github.com/pgvector/pgvector#indexing)

---

**Need Help?** Check the main project README or open an issue.
