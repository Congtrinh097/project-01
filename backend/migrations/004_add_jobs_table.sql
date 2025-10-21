-- Migration: Add jobs table
-- Description: Create table for storing individual job records extracted from URLs

-- Create jobs table
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_position ON jobs(position);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_working_type ON jobs(working_type);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_extraction_id ON jobs(extraction_id);

-- Add foreign key constraint to job_extractions table (optional)
-- ALTER TABLE jobs ADD CONSTRAINT fk_jobs_extraction_id 
--     FOREIGN KEY (extraction_id) REFERENCES job_extractions(id) ON DELETE SET NULL;

-- Add comments to table and columns
COMMENT ON TABLE jobs IS 'Individual job records extracted from job posting URLs';
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
COMMENT ON COLUMN jobs.created_at IS 'When this record was created';
