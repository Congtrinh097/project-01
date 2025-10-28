-- ============================================
-- COMPLETE DATABASE MIGRATION FOR CV ANALYZER
-- ============================================
-- Copy and paste this entire script into Supabase SQL Editor
-- This will set up all required tables, indexes, and extensions

-- ============================================
-- 1. Enable Required Extensions
-- ============================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 2. Create CVs Table
-- ============================================

CREATE TABLE IF NOT EXISTS cvs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    summary_pros TEXT,
    summary_cons TEXT,
    extracted_text TEXT,
    embedding vector(1536)
);

-- ============================================
-- 3. Create Resumes Table
-- ============================================

CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    pdf_path VARCHAR(500) NOT NULL,
    pdf_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. Create Jobs Table
-- ============================================

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    extraction_id INTEGER,
    position VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    job_link VARCHAR(500) NOT NULL,
    location VARCHAR(255),
    working_type VARCHAR(100),
    skills JSON,
    responsibilities JSON,
    education VARCHAR(255),
    experience VARCHAR(255),
    technical_skills JSON,
    soft_skills JSON,
    benefits JSON,
    company_size VARCHAR(100),
    why_join JSON,
    posted TIMESTAMP WITH TIME ZONE,
    summary TEXT,
    tags JSON,
    summary_embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 5. Create Indexes for Performance
-- ============================================

-- CV indexes
CREATE INDEX IF NOT EXISTS cvs_embedding_idx 
ON cvs USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX IF NOT EXISTS cvs_upload_time_idx 
ON cvs (upload_time DESC);

CREATE INDEX IF NOT EXISTS cvs_filename_idx 
ON cvs (filename);

-- Resume indexes
CREATE INDEX IF NOT EXISTS resumes_created_at_idx 
ON resumes (created_at DESC);

-- Job indexes
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_position ON jobs(position);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_working_type ON jobs(working_type);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_extraction_id ON jobs(extraction_id);

-- Vector similarity search for job summaries
CREATE INDEX IF NOT EXISTS idx_jobs_summary_embedding 
ON jobs USING ivfflat (summary_embedding vector_cosine_ops) 
WITH (lists = 100);

-- ============================================
-- 6. Add Comments for Documentation
-- ============================================

COMMENT ON TABLE cvs IS 'Stores uploaded CV/resume files and their AI analysis';
COMMENT ON TABLE resumes IS 'Stores AI-generated resumes created by users';
COMMENT ON TABLE jobs IS 'Individual job records extracted from job posting URLs';

-- CV table comments
COMMENT ON COLUMN cvs.id IS 'Unique identifier for each CV';
COMMENT ON COLUMN cvs.filename IS 'Original filename of uploaded CV';
COMMENT ON COLUMN cvs.file_path IS 'Storage path of the CV file';
COMMENT ON COLUMN cvs.file_size IS 'Size of the CV file in bytes';
COMMENT ON COLUMN cvs.upload_time IS 'Timestamp when CV was uploaded';
COMMENT ON COLUMN cvs.summary_pros IS 'AI-generated strengths from CV analysis';
COMMENT ON COLUMN cvs.summary_cons IS 'AI-generated areas for improvement from CV analysis';
COMMENT ON COLUMN cvs.extracted_text IS 'Full text content extracted from CV file';
COMMENT ON COLUMN cvs.embedding IS 'Vector embedding (1536 dimensions) from OpenAI text-embedding-3-small model for semantic search';

-- Resume table comments
COMMENT ON COLUMN resumes.id IS 'Unique identifier for each generated resume';
COMMENT ON COLUMN resumes.input_text IS 'User input text used to generate the resume';
COMMENT ON COLUMN resumes.generated_text IS 'AI-generated resume content';
COMMENT ON COLUMN resumes.pdf_path IS 'Storage path of the generated PDF file';
COMMENT ON COLUMN resumes.pdf_filename IS 'Filename of the generated PDF';
COMMENT ON COLUMN resumes.file_size IS 'Size of the generated PDF in bytes';
COMMENT ON COLUMN resumes.created_at IS 'Timestamp when resume was generated';

-- Job table comments
COMMENT ON COLUMN jobs.extraction_id IS 'Reference to the job extraction batch (optional)';
COMMENT ON COLUMN jobs.position IS 'Job position/title';
COMMENT ON COLUMN jobs.company IS 'Company name';
COMMENT ON COLUMN jobs.job_link IS 'Original job posting URL';
COMMENT ON COLUMN jobs.location IS 'Job location';
COMMENT ON COLUMN jobs.working_type IS 'Type of work (Full-time, Part-time, etc.)';
COMMENT ON COLUMN jobs.skills IS 'Array of required skills';
COMMENT ON COLUMN jobs.responsibilities IS 'Array of job responsibilities';
COMMENT ON COLUMN jobs.education IS 'Education requirements';
COMMENT ON COLUMN jobs.experience IS 'Experience requirements';
COMMENT ON COLUMN jobs.technical_skills IS 'Array of technical skills';
COMMENT ON COLUMN jobs.soft_skills IS 'Array of soft skills';
COMMENT ON COLUMN jobs.benefits IS 'Array of job benefits';
COMMENT ON COLUMN jobs.company_size IS 'Company size information';
COMMENT ON COLUMN jobs.why_join IS 'Array of reasons to join the company';
COMMENT ON COLUMN jobs.posted IS 'When the job was posted';
COMMENT ON COLUMN jobs.summary IS 'Job summary/description';
COMMENT ON COLUMN jobs.tags IS 'Array of classification tags';
COMMENT ON COLUMN jobs.summary_embedding IS 'OpenAI embedding vector for job summary to enable semantic search';
COMMENT ON COLUMN jobs.created_at IS 'When this record was created';

-- ============================================
-- 7. Verification Queries
-- ============================================

-- Check if pgvector extension is enabled
SELECT 'pgvector extension status:' as status, 
       CASE WHEN EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector') 
            THEN 'ENABLED' 
            ELSE 'NOT ENABLED' 
       END as result;

-- List all tables
SELECT 'Tables created:' as status, 
       string_agg(tablename, ', ' ORDER BY tablename) as tables
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('cvs', 'resumes', 'jobs');

-- Check table structures
SELECT 'CVs table columns:' as table_name, 
       string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'cvs' AND table_schema = 'public';

SELECT 'Resumes table columns:' as table_name, 
       string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'resumes' AND table_schema = 'public';

SELECT 'Jobs table columns:' as table_name, 
       string_agg(column_name, ', ' ORDER BY ordinal_position) as columns
FROM information_schema.columns 
WHERE table_name = 'jobs' AND table_schema = 'public';

-- Count records in each table
SELECT 'CVs count:' as table_name, COUNT(*) as record_count FROM cvs
UNION ALL
SELECT 'Resumes count:' as table_name, COUNT(*) as record_count FROM resumes
UNION ALL
SELECT 'Jobs count:' as table_name, COUNT(*) as record_count FROM jobs;

-- ============================================
-- MIGRATION COMPLETE!
-- ============================================

SELECT '🎉 Database migration completed successfully!' as status;
