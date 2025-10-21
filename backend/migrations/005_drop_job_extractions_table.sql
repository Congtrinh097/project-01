-- Migration: Drop job_extractions table
-- Description: Remove the job_extractions table as we now only use the jobs table

-- Drop the job_extractions table
DROP TABLE IF EXISTS job_extractions;

-- Add comment
COMMENT ON TABLE job_extractions IS 'Table has been removed - jobs are now stored directly in the jobs table';
