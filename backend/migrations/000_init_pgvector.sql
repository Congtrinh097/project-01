-- This script runs automatically when PostgreSQL container starts for the first time
-- It's executed before 001_add_embedding_support.sql (alphabetical order)

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

