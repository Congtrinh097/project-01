-- Complete Database Schema Migration for CV Analyzer
-- This script creates all required tables and indexes
-- Run this in your Supabase SQL Editor or PostgreSQL database

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
-- 4. Create Indexes for Performance
-- ============================================

-- Index for CV vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS cvs_embedding_idx 
ON cvs USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for faster CV queries by upload time
CREATE INDEX IF NOT EXISTS cvs_upload_time_idx 
ON cvs (upload_time DESC);

-- Index for faster CV queries by filename
CREATE INDEX IF NOT EXISTS cvs_filename_idx 
ON cvs (filename);

-- Index for faster resume queries by creation time
CREATE INDEX IF NOT EXISTS resumes_created_at_idx 
ON resumes (created_at DESC);

-- ============================================
-- 5. Add Comments for Documentation
-- ============================================

COMMENT ON TABLE cvs IS 'Stores uploaded CV/resume files and their AI analysis';
COMMENT ON TABLE resumes IS 'Stores AI-generated resumes created by users';

COMMENT ON COLUMN cvs.id IS 'Unique identifier for each CV';
COMMENT ON COLUMN cvs.filename IS 'Original filename of uploaded CV';
COMMENT ON COLUMN cvs.file_path IS 'Storage path of the CV file';
COMMENT ON COLUMN cvs.file_size IS 'Size of the CV file in bytes';
COMMENT ON COLUMN cvs.upload_time IS 'Timestamp when CV was uploaded';
COMMENT ON COLUMN cvs.summary_pros IS 'AI-generated strengths from CV analysis';
COMMENT ON COLUMN cvs.summary_cons IS 'AI-generated areas for improvement from CV analysis';
COMMENT ON COLUMN cvs.extracted_text IS 'Full text content extracted from CV file';
COMMENT ON COLUMN cvs.embedding IS 'Vector embedding (1536 dimensions) from OpenAI text-embedding-3-small model for semantic search';

COMMENT ON COLUMN resumes.id IS 'Unique identifier for each generated resume';
COMMENT ON COLUMN resumes.input_text IS 'User input text used to generate the resume';
COMMENT ON COLUMN resumes.generated_text IS 'AI-generated resume content';
COMMENT ON COLUMN resumes.pdf_path IS 'Storage path of the generated PDF file';
COMMENT ON COLUMN resumes.pdf_filename IS 'Filename of the generated PDF';
COMMENT ON COLUMN resumes.file_size IS 'Size of the generated PDF in bytes';
COMMENT ON COLUMN resumes.created_at IS 'Timestamp when resume was generated';

-- ============================================
-- 6. Grant Permissions (Optional - for specific users)
-- ============================================

-- Grant permissions to authenticated users (Supabase)
-- GRANT ALL ON cvs TO authenticated;
-- GRANT ALL ON resumes TO authenticated;
-- GRANT USAGE, SELECT ON SEQUENCE cvs_id_seq TO authenticated;
-- GRANT USAGE, SELECT ON SEQUENCE resumes_id_seq TO authenticated;

-- For PostgreSQL with specific user (replace 'your_user' with actual username)
-- GRANT ALL PRIVILEGES ON cvs TO your_user;
-- GRANT ALL PRIVILEGES ON resumes TO your_user;

-- ============================================
-- 7. Verification Queries
-- ============================================

-- Check if pgvector extension is enabled
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- List all tables
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Check table structure
-- \d cvs
-- \d resumes

-- Count records
-- SELECT COUNT(*) FROM cvs;
-- SELECT COUNT(*) FROM resumes;

-- ============================================
-- Migration Complete!
-- ============================================

