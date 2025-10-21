-- Migration: Add summary_embedding field to jobs table
-- Description: Add vector embedding field for job summaries to enable semantic search

-- Add summary_embedding column to jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS summary_embedding vector(1536);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_jobs_summary_embedding ON jobs USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);

-- Add comment to the new column
COMMENT ON COLUMN jobs.summary_embedding IS 'OpenAI embedding vector for job summary to enable semantic search';
