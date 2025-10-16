-- Migration: Add pgvector support and embedding columns to cvs table
-- Note: pgvector extension is already enabled in 000_init_pgvector.sql

-- Add new columns to cvs table
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS extracted_text TEXT,
ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Create index for vector similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS cvs_embedding_idx ON cvs USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: Create index for L2 distance (if preferred)
-- CREATE INDEX IF NOT EXISTS cvs_embedding_l2_idx ON cvs USING ivfflat (embedding vector_l2_ops);

-- Note: For small datasets (< 1000 rows), you can skip the index or use a smaller 'lists' value
-- For larger datasets, adjust 'lists' parameter: recommended value is rows/1000

COMMENT ON COLUMN cvs.extracted_text IS 'Full text content extracted from CV file';
COMMENT ON COLUMN cvs.embedding IS 'Vector embedding (1536 dimensions) from OpenAI text-embedding-3-small model';

