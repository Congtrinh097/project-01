-- Quick Database Setup for CV Analyzer
-- Copy and paste this into Supabase SQL Editor or run with psql

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create CVs table
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

-- Create Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    pdf_path VARCHAR(500) NOT NULL,
    pdf_filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS cvs_embedding_idx ON cvs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS cvs_upload_time_idx ON cvs (upload_time DESC);
CREATE INDEX IF NOT EXISTS resumes_created_at_idx ON resumes (created_at DESC);

-- Done! Run these queries to verify:
-- SELECT * FROM pg_extension WHERE extname = 'vector';
-- SELECT COUNT(*) FROM cvs;
-- SELECT COUNT(*) FROM resumes;

