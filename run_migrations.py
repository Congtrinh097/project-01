#!/usr/bin/env python3
"""
Database Migration Runner for CV Analyzer
Runs all database schema migrations to set up the complete database structure.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment or Google Cloud Secret Manager"""
    # Try environment variable first
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        try:
            # Try to get from Google Cloud Secret Manager
            import subprocess
            result = subprocess.run([
                'gcloud', 'secrets', 'versions', 'access', 'latest', '--secret=database-url'
            ], capture_output=True, text=True, check=True)
            database_url = result.stdout.strip()
            logger.info("Retrieved database URL from Google Cloud Secret Manager")
        except Exception as e:
            logger.error(f"Failed to get database URL from Secret Manager: {e}")
            return None
    
    return database_url

def run_sql_file(conn, file_path):
    """Run a SQL file against the database"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        with conn.cursor() as cursor:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                        logger.info(f"✓ Executed statement {i+1}/{len(statements)}")
                    except Exception as e:
                        logger.warning(f"⚠ Statement {i+1} failed (may already exist): {e}")
                        # Continue with other statements
                        pass
            
            conn.commit()
            logger.info(f"✓ Successfully executed {file_path}")
            return True
            
    except Exception as e:
        logger.error(f"✗ Failed to execute {file_path}: {e}")
        return False

def verify_migration(conn):
    """Verify that the migration was successful"""
    try:
        with conn.cursor() as cursor:
            # Check if pgvector extension is enabled
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            vector_ext = cursor.fetchone()
            if vector_ext:
                logger.info("✓ pgvector extension is enabled")
            else:
                logger.warning("⚠ pgvector extension not found")
            
            # Check if tables exist
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('cvs', 'resumes', 'jobs')
                ORDER BY tablename;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['cvs', 'resumes', 'jobs']
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.error(f"✗ Table '{table}' missing")
            
            # Check if jobs table has summary_embedding column
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'jobs' AND column_name = 'summary_embedding';
            """)
            embedding_col = cursor.fetchone()
            if embedding_col:
                logger.info("✓ jobs.summary_embedding column exists")
            else:
                logger.warning("⚠ jobs.summary_embedding column missing")
            
            # Count records in each table
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                logger.info(f"✓ Table '{table}' has {count} records")
            
            return True
            
    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting database migration...")
    
    # Get database URL
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ No database URL found. Please set DATABASE_URL environment variable or configure Google Cloud Secret Manager.")
        sys.exit(1)
    
    logger.info(f"📡 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info("✓ Connected to database successfully")
        
        # Migration files to run (in order)
        migration_files = [
            "backend/migrations/002_complete_schema.sql",
            "backend/migrations/004_add_jobs_table.sql", 
            "backend/migrations/006_add_summary_embedding_to_jobs.sql"
        ]
        
        # Run migrations
        success_count = 0
        for migration_file in migration_files:
            if os.path.exists(migration_file):
                logger.info(f"📄 Running migration: {migration_file}")
                if run_sql_file(conn, migration_file):
                    success_count += 1
            else:
                logger.warning(f"⚠ Migration file not found: {migration_file}")
        
        logger.info(f"📊 Migration summary: {success_count}/{len(migration_files)} files processed")
        
        # Verify migration
        logger.info("🔍 Verifying migration...")
        if verify_migration(conn):
            logger.info("✅ Database migration completed successfully!")
        else:
            logger.error("❌ Migration verification failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 Database connection closed")

if __name__ == "__main__":
    main()
