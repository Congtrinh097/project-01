import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

class JobExtractor:
    """
    Service for extracting job information from URLs using OpenAI
    """
    
    def __init__(self):
        """Initialize the job extractor with OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.model_name = "gpt-4o-mini"
        
        if not self.client:
            logger.warning("OpenAI API key not configured. Job extraction will not work.")
    
    def build_prompt(self, job_urls: List[str]) -> str:
        """
        Build the dynamic extraction prompt for job URLs
        
        Args:
            job_urls: List of job posting URLs
            
        Returns:
            Formatted prompt string
        """
        urls_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(job_urls)])
        
        return f"""
Extract all job posting information from the following URLs:

{urls_text}

Return your result as a JSON object with this structure:
{{
  "jobs": [
    {{
      "position": "",
      "company": "",
      "job_link": "",
      "location": "",
      "working_type": "",
      "skills": [],
      "responsibilities": [],
      "requirements": {{
        "education": "",
        "experience": "",
        "technical_skills": [],
        "soft_skills": []
      }},
      "benefits": [],
      "company_size": "",
      "why_join": [],
      "posted": "<ISO 8601 datetime>",
      "summary": "",
      "tags": []
    }}
  ]
}}

Guidelines:
- Extract and clean all key information for each job.
- Add 'tags': a list of up to 10 concise, relevant classification tags (e.g., 'AI', 'Machine Learning', 'Frontend', 'Backend', 'Fintech', 'Data Science').
- Return ISO 8601 datetime for 'posted'.
- Write the summary in Vietnamese if the page is in Vietnamese.
- Return only the JSON object with no additional text.
"""
    
    async def extract_jobs(self, job_urls: List[str], db=None) -> Dict[str, Any]:
        """
        Extract job information from URLs using OpenAI and save to database
        
        Args:
            job_urls: List of job posting URLs
            db: Database session for saving jobs
            
        Returns:
            Dictionary containing extracted data, count, and saved job IDs
            
        Raises:
            Exception: If extraction fails or OpenAI API key is not configured
        """
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        if not job_urls:
            raise ValueError("No URLs provided")
        
        logger.info(f"Extracting jobs from {len(job_urls)} URLs")
        
        try:
            prompt = self.build_prompt(job_urls)
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant that returns only valid JSON. Always return a JSON object with a 'jobs' key containing an array of job objects."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                parsed_response = json.loads(result)
                
                # Extract jobs array from the response
                if "jobs" not in parsed_response:
                    logger.error(f"No 'jobs' key found in response: {result}")
                    raise Exception("Invalid response format: missing 'jobs' key")
                
                jobs_data = parsed_response["jobs"]
                
                if not isinstance(jobs_data, list):
                    logger.error(f"'jobs' key is not an array: {jobs_data}")
                    raise Exception("Invalid response format: 'jobs' must be an array")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON returned from model: {result}")
                raise Exception("Invalid JSON returned from model")
            
            logger.info(f"Successfully extracted {len(jobs_data)} jobs")
            
            # Save individual jobs to database if db session is provided
            saved_job_ids = []
            failed_jobs = []
            
            if db:
                from models import Job
                
                for job_data in jobs_data:
                    job_position = job_data.get('position', 'Unknown')
                    job_company = job_data.get('company', 'Unknown')
                    
                    try:
                        # Parse posted date if available
                        posted_date = None
                        if job_data.get("posted"):
                            try:
                                posted_date = datetime.fromisoformat(job_data["posted"].replace('Z', '+00:00'))
                            except (ValueError, AttributeError):
                                logger.warning(f"Could not parse posted date: {job_data.get('posted')}")
                        
                        # Extract requirements data
                        requirements = job_data.get("requirements", {})
                        
                        # Generate embedding from combined job information (REQUIRED)
                        summary_embedding = None
                        combined_text = self.build_embedding_text(job_data, requirements)
                        
                        if not combined_text:
                            error_msg = "No combined text available for embedding generation"
                            logger.error(f"Job '{job_position}' at '{job_company}': {error_msg}")
                            failed_jobs.append({
                                "position": job_position,
                                "company": job_company,
                                "error": error_msg
                            })
                            continue
                        
                        try:
                            logger.info(f"Generating embedding for job: {job_position} at {job_company}")
                            summary_embedding = self.generate_embedding(combined_text)
                        except Exception as e:
                            error_msg = f"Failed to generate embedding: {str(e)}"
                            logger.error(f"Job '{job_position}' at '{job_company}': {error_msg}")
                            failed_jobs.append({
                                "position": job_position,
                                "company": job_company,
                                "error": error_msg
                            })
                            continue
                        
                        # Check if embedding was successfully generated
                        if not summary_embedding or len(summary_embedding) == 0:
                            error_msg = "Embedding generation returned empty result"
                            logger.error(f"Job '{job_position}' at '{job_company}': {error_msg}")
                            failed_jobs.append({
                                "position": job_position,
                                "company": job_company,
                                "error": error_msg
                            })
                            continue
                        
                        # Create Job record (only if embedding is successful)
                        job_record = Job(
                            position=job_data.get("position", ""),
                            company=job_data.get("company", ""),
                            job_link=job_data.get("job_link", ""),
                            location=job_data.get("location"),
                            working_type=job_data.get("working_type"),
                            skills=job_data.get("skills", []),
                            responsibilities=job_data.get("responsibilities", []),
                            education=requirements.get("education"),
                            experience=requirements.get("experience"),
                            technical_skills=requirements.get("technical_skills", []),
                            soft_skills=requirements.get("soft_skills", []),
                            benefits=job_data.get("benefits", []),
                            company_size=job_data.get("company_size"),
                            why_join=job_data.get("why_join", []),
                            posted=posted_date,
                            summary=job_data.get("summary"),
                            tags=job_data.get("tags", []),
                            summary_embedding=summary_embedding,
                            created_at=datetime.utcnow()
                        )
                        
                        db.add(job_record)
                        db.flush()  # Flush to get the ID
                        saved_job_ids.append(job_record.id)
                        logger.info(f"Successfully saved job '{job_position}' at '{job_company}' with ID {job_record.id}")
                        
                    except Exception as e:
                        error_msg = f"Error saving job to database: {str(e)}"
                        logger.error(f"Job '{job_position}' at '{job_company}': {error_msg}")
                        failed_jobs.append({
                            "position": job_position,
                            "company": job_company,
                            "error": error_msg
                        })
                        continue
                
                # Commit all successfully processed jobs
                if saved_job_ids:
                    db.commit()
                    logger.info(f"Successfully saved {len(saved_job_ids)} jobs to database")
                else:
                    logger.warning("No jobs were saved to database")
            
            # Build response with success and failure information
            response = {
                "data": jobs_data,
                "count": len(jobs_data),
                "saved_count": len(saved_job_ids),
                "failed_count": len(failed_jobs),
                "saved_job_ids": saved_job_ids,
                "failed_jobs": failed_jobs
            }
            
            # If all jobs failed, raise an exception
            if failed_jobs and len(failed_jobs) == len(jobs_data):
                error_details = "\n".join([f"- {job['position']} at {job['company']}: {job['error']}" for job in failed_jobs])
                raise Exception(f"All {len(failed_jobs)} jobs failed to save:\n{error_details}")
            
            # If some jobs failed, log a warning
            if failed_jobs:
                logger.warning(f"{len(failed_jobs)} out of {len(jobs_data)} jobs failed to save due to embedding errors")
            
            return response
            
        except Exception as e:
            logger.error(f"Error extracting jobs: {str(e)}")
            raise Exception(f"Job extraction failed: {str(e)}")
    
    def build_embedding_text(self, job_data: Dict[str, Any], requirements: Dict[str, Any]) -> str:
        """
        Build comprehensive text from job data for embedding generation
        
        Args:
            job_data: Job information dictionary
            requirements: Requirements information dictionary
            
        Returns:
            Combined text string containing all meaningful job information
        """
        text_parts = []
        
        # Position and Company
        if job_data.get("position"):
            text_parts.append(f"Position: {job_data['position']}")
        if job_data.get("company"):
            text_parts.append(f"Company: {job_data['company']}")
        
        # Location and Working Type
        if job_data.get("location"):
            text_parts.append(f"Location: {job_data['location']}")
        if job_data.get("working_type"):
            text_parts.append(f"Working Type: {job_data['working_type']}")
        
        # Skills
        if job_data.get("skills"):
            skills_text = ", ".join(job_data["skills"])
            text_parts.append(f"Skills: {skills_text}")
        
        # Requirements - Education and Experience
        if requirements.get("education"):
            text_parts.append(f"Education: {requirements['education']}")
        if requirements.get("experience"):
            text_parts.append(f"Experience: {requirements['experience']}")
        
        # Technical Skills
        if requirements.get("technical_skills"):
            tech_skills_text = ", ".join(requirements["technical_skills"])
            text_parts.append(f"Technical Skills: {tech_skills_text}")
        
        # Soft Skills
        if requirements.get("soft_skills"):
            soft_skills_text = ", ".join(requirements["soft_skills"])
            text_parts.append(f"Soft Skills: {soft_skills_text}")
        
        # Responsibilities
        if job_data.get("responsibilities"):
            resp_text = ". ".join(job_data["responsibilities"][:3])  # First 3 responsibilities
            text_parts.append(f"Responsibilities: {resp_text}")
        
        # Benefits
        if job_data.get("benefits"):
            benefits_text = ", ".join(job_data["benefits"][:5])  # First 5 benefits
            text_parts.append(f"Benefits: {benefits_text}")
        
        # Company Size
        if job_data.get("company_size"):
            text_parts.append(f"Company Size: {job_data['company_size']}")
        
        # Why Join
        if job_data.get("why_join"):
            why_join_text = ". ".join(job_data["why_join"][:3])  # First 3 reasons
            text_parts.append(f"Why Join: {why_join_text}")
        
        # Summary
        if job_data.get("summary"):
            text_parts.append(f"Summary: {job_data['summary']}")
        
        # Tags
        if job_data.get("tags"):
            tags_text = ", ".join(job_data["tags"])
            text_parts.append(f"Tags: {tags_text}")
        
        # Combine all parts with newlines
        combined_text = "\n".join(text_parts)
        
        logger.debug(f"Built embedding text with {len(text_parts)} components, total length: {len(combined_text)}")
        
        return combined_text.strip() if combined_text else None
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using OpenAI
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If embedding generation fails
        """
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
        if not text or not text.strip():
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text.strip()
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def is_configured(self) -> bool:
        """
        Check if the service is properly configured
        
        Returns:
            True if OpenAI client is configured, False otherwise
        """
        return self.client is not None
