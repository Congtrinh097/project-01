-- Migration: Add job_extractions table
-- Description: Create table for storing job extraction results from URLs

-- Create job_extractions table
CREATE TABLE IF NOT EXISTS job_extractions (
    id SERIAL PRIMARY KEY,
    urls JSON NOT NULL,
    extracted_data JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on created_at for better query performance
CREATE INDEX IF NOT EXISTS idx_job_extractions_created_at ON job_extractions(created_at);

-- Add comment to table
COMMENT ON TABLE job_extractions IS 'Stores job extraction results from URLs using AI';
COMMENT ON COLUMN job_extractions.urls IS 'Array of job posting URLs that were processed';
COMMENT ON COLUMN job_extractions.extracted_data IS 'JSON array of extracted job information';
COMMENT ON COLUMN job_extractions.created_at IS 'Timestamp when the extraction was performed';
