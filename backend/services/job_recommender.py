import openai
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import settings

logger = logging.getLogger(__name__)


class JobRecommender:
    def __init__(self):
        # Use separate API key for embeddings, fall back to main key if not set
        embed_api_key = settings.OPENAI_EMBED_API_KEY or settings.OPENAI_API_KEY
        
        if not embed_api_key:
            raise ValueError("OpenAI API key is required (OPENAI_EMBED_API_KEY or OPENAI_API_KEY)")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required for chat completions")
        
        # Get base URL from settings or use default
        base_url = getattr(settings, 'OPENAI_BASE_URL', None)
        
        # Client for embeddings
        if base_url:
            self.embed_client = openai.OpenAI(api_key=embed_api_key, base_url=base_url)
        else:
            self.embed_client = openai.OpenAI(api_key=embed_api_key)
        
        # Client for chat completions
        if base_url:
            self.chat_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url=base_url)
        else:
            self.chat_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-4o-mini"
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text using OpenAI
        
        Args:
            text: Text content to embed
            
        Returns:
            List of floats representing the embedding vector (1536 dimensions)
        """
        try:
            # Truncate text if too long (max ~8000 tokens for embedding model)
            max_chars = 30000  # Roughly 8000 tokens
            if len(text) > max_chars:
                text = text[:max_chars]
            
            response = self.embed_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise ValueError(f"Failed to generate embedding: {str(e)}")
    
    def find_similar_jobs(
        self, 
        query_embedding: List[float], 
        db: Session, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find jobs most similar to the query embedding using cosine similarity
        
        Args:
            query_embedding: Query vector embedding
            db: Database session
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing job data and similarity scores
        """
        try:
            # Convert embedding list to PostgreSQL vector format
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Use raw SQL with string interpolation for pgvector
            query_sql = f"""
                SELECT 
                    id,
                    position,
                    company,
                    job_link,
                    location,
                    working_type,
                    skills,
                    responsibilities,
                    education,
                    experience,
                    technical_skills,
                    soft_skills,
                    benefits,
                    company_size,
                    why_join,
                    posted,
                    summary,
                    tags,
                    created_at,
                    1 - (summary_embedding <=> '{embedding_str}'::vector) as similarity_score
                FROM jobs
                WHERE summary_embedding IS NOT NULL
                ORDER BY summary_embedding <=> '{embedding_str}'::vector
                LIMIT :limit
            """
            
            result = db.execute(
                text(query_sql),
                {"limit": limit}
            )
            
            similar_jobs = []
            for row in result:
                similar_jobs.append({
                    "id": row.id,
                    "position": row.position,
                    "company": row.company,
                    "job_link": row.job_link,
                    "location": row.location,
                    "working_type": row.working_type,
                    "skills": row.skills,
                    "responsibilities": row.responsibilities,
                    "education": row.education,
                    "experience": row.experience,
                    "technical_skills": row.technical_skills,
                    "soft_skills": row.soft_skills,
                    "benefits": row.benefits,
                    "company_size": row.company_size,
                    "why_join": row.why_join,
                    "posted": row.posted,
                    "summary": row.summary,
                    "tags": row.tags,
                    "created_at": row.created_at,
                    "similarity_score": float(row.similarity_score)
                })
            
            logger.info(f"Found {len(similar_jobs)} similar jobs")
            return similar_jobs
            
        except Exception as e:
            logger.error(f"Error finding similar jobs: {str(e)}")
            raise ValueError(f"Failed to search similar jobs: {str(e)}")
    
    def _generate_low_similarity_message(self, query: str) -> str:
        """
        Generate a helpful message when no jobs meet the 30% similarity threshold
        
        Args:
            query: Original user query or CV content
            
        Returns:
            Helpful message in appropriate language
        """
        try:
            prompt = f"""
You are a career advisor. The user is looking for job opportunities but no jobs in the database match their profile or requirements (all similarity scores are below 30%).

User Query/CV: "{query[:500]}..."

Generate a polite, helpful message that:
1. Apologizes that no matching jobs were found for their specific profile/requirements
2. Suggests they try rephrasing or broadening their search criteria
3. Provides 2-3 specific tips on how to improve their search or update their profile

LANGUAGE INSTRUCTIONS:
- If the user query is in Vietnamese, respond entirely in Vietnamese
- If the user query is in English, respond entirely in English
- If the query is in another language, respond in that language
- Match the tone and formality of the query

Keep the message concise and actionable (max 150 words).
"""
            
            response = self.chat_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful career advisor that communicates clearly in multiple languages, adapting to the user's language."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating low similarity message: {str(e)}")
            # Fallback message in English
            return """Sorry, we couldn't find any jobs that closely match your profile or requirements (similarity < 30%).

Suggestions to improve your search:
- Try using broader or different keywords
- Focus on core skills rather than specific combinations
- Consider related job titles or industries
- Update your profile with more relevant skills

Please refine your query and try again."""
    
    def generate_ai_recommendation(
        self, 
        query: str, 
        similar_jobs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate AI-powered job recommendation summary based on search results
        
        Args:
            query: Original user query or CV content
            similar_jobs: List of similar job results
            
        Returns:
            AI-generated recommendation text
        """
        try:
            # Prepare context from similar jobs
            job_summaries = []
            for i, job in enumerate(similar_jobs[:5], 1):
                # Format skills nicely
                skills_str = ", ".join(job.get('technical_skills', [])[:5]) if job.get('technical_skills') else "N/A"
                
                summary = f"""
Job {i}: {job.get('position', 'Unknown')} at {job.get('company', 'Unknown')}
Similarity Score: {job.get('similarity_score', 0):.2f}
Location: {job.get('location', 'N/A')}
Working Type: {job.get('working_type', 'N/A')}
Experience Required: {job.get('experience', 'N/A')}
Education: {job.get('education', 'N/A')}
Key Technical Skills: {skills_str}
Summary: {job.get('summary', 'N/A')[:300]}...
"""
                job_summaries.append(summary)
            
            context = "\n\n".join(job_summaries)
            
            # Determine if query is a CV or search text
            is_cv = len(query) > 500  # Assume longer text is a CV
            
            # Create prompt for AI recommendation
            if is_cv:
                prompt = f"""
You are an expert career advisor helping to find the best job opportunities for a candidate based on their CV/profile.

Candidate CV/Profile Summary: "{query[:1000]}..."

Top Matching Jobs:
{context}

Based on the candidate's profile and the matching jobs above, provide:
1. A brief overview of the job matches found
2. Why these jobs are good fits for the candidate's profile
3. Key highlights of each top match (company, position, requirements)
4. A recommendation on which job(s) to apply for first and why
5. Any gaps or additional skills the candidate should consider developing

LANGUAGE INSTRUCTIONS:
- If the CV/profile is in Vietnamese, provide your entire response in Vietnamese
- If the CV/profile is in English, respond entirely in English
- When presenting job summaries, translate or paraphrase them to match the CV language

Keep your response professional, encouraging, and actionable (max 350 words per language).
"""
            else:
                prompt = f"""
You are an expert career advisor helping to find the best job opportunities based on search criteria.

Search Query: "{query}"

Top Matching Jobs:
{context}

Based on the search query and the matching jobs above, provide:
1. A brief overview of what was found
2. Why these jobs match the search criteria
3. Key highlights of each top match (company, position, benefits, requirements)
4. A recommendation on which job(s) to consider first

LANGUAGE INSTRUCTIONS:
- If the search query is in Vietnamese, provide your entire response in Vietnamese
- If the search query is in English, respond entirely in English
- When presenting job summaries, translate or paraphrase them to match the query language

Keep your response concise, professional, and actionable (max 300 words per language).
"""
            
            response = self.chat_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career advisor specializing in job matching and career development. You can communicate fluently in both Vietnamese and English, adapting your language to match the user's input."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            recommendation = response.choices[0].message.content
            logger.info("Generated AI job recommendation successfully")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {str(e)}")
            return "Unable to generate AI recommendation at this time."
    
    def search_and_recommend(
        self, 
        query: str, 
        db: Session, 
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Complete workflow: Generate embedding, search jobs, and create recommendation
        
        Args:
            query: User search query or CV text
            db: Database session
            limit: Number of results to return
            
        Returns:
            Dictionary with query, results, and AI recommendation
        """
        try:
            # Step 1: Generate embedding for query
            logger.info(f"Processing job search query: {query[:100]}...")
            query_embedding = self.generate_embedding(query)
            
            # Step 2: Find similar jobs
            similar_jobs = self.find_similar_jobs(query_embedding, db, limit)
            
            if not similar_jobs:
                return {
                    "query": query[:200] + "..." if len(query) > 200 else query,
                    "results": [],
                    "ai_recommendation": "No matching jobs found in the database. Please add some jobs first or try a different search."
                }
            
            # Step 2.5: Check if similarity scores are too low (< 30%)
            max_similarity = max(job.get('similarity_score', 0) for job in similar_jobs)
            if max_similarity < 0.3:
                # Generate a helpful message based on query language
                sorry_message = self._generate_low_similarity_message(query)
                return {
                    "query": query[:200] + "..." if len(query) > 200 else query,
                    "results": [],
                    "ai_recommendation": sorry_message
                }
            
            # Step 3: Generate AI recommendation
            ai_recommendation = self.generate_ai_recommendation(query, similar_jobs)
            
            # Step 4: Format results
            formatted_results = []
            for job in similar_jobs:
                formatted_results.append({
                    "id": job['id'],
                    "position": job['position'],
                    "company": job['company'],
                    "job_link": job['job_link'],
                    "location": job.get('location'),
                    "working_type": job.get('working_type'),
                    "experience": job.get('experience'),
                    "education": job.get('education'),
                    "technical_skills": job.get('technical_skills', []),
                    "soft_skills": job.get('soft_skills', []),
                    "benefits": job.get('benefits', []),
                    "tags": job.get('tags', []),
                    "summary": job.get('summary', ''),
                    "similarity_score": round(job['similarity_score'], 4),
                    "posted": job['posted'].isoformat() if job.get('posted') else None,
                    "created_at": job['created_at'].isoformat() if job.get('created_at') else None
                })
            
            return {
                "query": query[:200] + "..." if len(query) > 200 else query,
                "results": formatted_results,
                "ai_recommendation": ai_recommendation
            }
            
        except Exception as e:
            logger.error(f"Error in job search and recommend workflow: {str(e)}")
            raise

