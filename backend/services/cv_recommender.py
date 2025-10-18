import openai
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from config import settings

logger = logging.getLogger(__name__)


class CVRecommender:
    def __init__(self):
        # Use separate API key for embeddings, fall back to main key if not set
        embed_api_key = settings.OPENAI_EMBED_API_KEY or settings.OPENAI_API_KEY
        
        if not embed_api_key:
            raise ValueError("OpenAI API key is required (OPENAI_EMBED_API_KEY or OPENAI_API_KEY)")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required for chat completions")
        
        # Client for embeddings
        self.embed_client = openai.OpenAI(
            api_key=embed_api_key,
            base_url="https://aiportalapi.stu-platform.live/jpe"
        )
        
        # Client for chat completions
        self.chat_client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url="https://aiportalapi.stu-platform.live/jpe"
        )
        
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
    
    def find_similar_cvs(
        self, 
        query_embedding: List[float], 
        db: Session, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find CVs most similar to the query embedding using cosine similarity
        
        Args:
            query_embedding: Query vector embedding
            db: Database session
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing CV data and similarity scores
        """
        try:
            # Convert embedding list to PostgreSQL vector format
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Use raw SQL with string interpolation for pgvector
            # Note: We use f-string for embedding_str (safe, as it's generated internally)
            # and parameterized query for limit (user input)
            query_sql = f"""
                SELECT 
                    id,
                    filename,
                    extracted_text,
                    summary_pros,
                    summary_cons,
                    upload_time,
                    1 - (embedding <=> '{embedding_str}'::vector) as similarity_score
                FROM cvs
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> '{embedding_str}'::vector
                LIMIT :limit
            """
            
            result = db.execute(
                text(query_sql),
                {"limit": limit}
            )
            
            similar_cvs = []
            for row in result:
                similar_cvs.append({
                    "id": row.id,
                    "filename": row.filename,
                    "extracted_text": row.extracted_text,
                    "summary_pros": row.summary_pros,
                    "summary_cons": row.summary_cons,
                    "upload_time": row.upload_time,
                    "similarity_score": float(row.similarity_score)
                })
            
            logger.info(f"Found {len(similar_cvs)} similar CVs")
            return similar_cvs
            
        except Exception as e:
            logger.error(f"Error finding similar CVs: {str(e)}")
            raise ValueError(f"Failed to search similar CVs: {str(e)}")
    
    def _generate_low_similarity_message(self, query: str) -> str:
        """
        Generate a helpful message when no CVs meet the 30% similarity threshold
        
        Args:
            query: Original user query
            
        Returns:
            Helpful message in appropriate language
        """
        try:
            prompt = f"""
                        You are an HR assistant. The user searched for candidates but no CVs in the database match their requirements (all similarity scores are below 30%).

                        User Query: "{query}"

                        Generate a polite, helpful message that:
                        1. Apologizes that no matching CVs were found for their specific requirements
                        2. Suggests they try rephrasing or broadening their search query
                        3. Provides 2-3 specific tips on how to improve their search (e.g., use different keywords, be less specific, focus on core skills)

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
                        "content": "You are a helpful HR assistant that communicates clearly in multiple languages, adapting to the user's language."
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
            return """Sorry, we couldn't find any CVs that closely match your requirements (similarity < 30%).

                    Suggestions to improve your search:
                    - Try using broader or different keywords
                    - Focus on core skills rather than specific combinations
                    - Simplify your search criteria
                    - Check if the required qualifications are too specific

                    Please refine your query and try again."""
    
    def generate_ai_recommendation(
        self, 
        query: str, 
        similar_cvs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate AI-powered recommendation summary based on search results
        
        Args:
            query: Original user query
            similar_cvs: List of similar CV results
            
        Returns:
            AI-generated recommendation text
        """
        try:
            # Prepare context from similar CVs
            cv_summaries = []
            for i, cv in enumerate(similar_cvs[:5], 1):
                # Truncate extracted text for context
                text_preview = cv.get('extracted_text', '')[:500]
                summary = f"""
                            CV {i}: {cv.get('filename', 'Unknown')}
                            Similarity Score: {cv.get('similarity_score', 0):.2f}
                            Preview: {text_preview}...
                            Strengths: {cv.get('summary_pros', 'N/A')[:200]}...
                            """
                cv_summaries.append(summary)
            
            context = "\n\n".join(cv_summaries)
            
            # Create prompt for AI recommendation
            prompt = f"""
You are an expert HR consultant helping to find the best candidates based on a search query.

User Query: "{query}"

Top Matching CVs:
{context}

Based on the search query and the matching CVs above, provide:
1. A brief overview of what was found
2. Why these candidates match the query
3. Key strengths and qualifications of the top matches (translate/summarize the CV strengths in the same language as the query)
4. A recommendation on which candidate(s) to consider first

LANGUAGE INSTRUCTIONS:
- If the user query is in Vietnamese, provide your entire response in Vietnamese (including CV summaries and strengths)
- If the user query is in English, respond entirely in English
- If the user query is in both Vietnamese and English, respond in both languages
- If the user query is in other languages, respond in the language of the user's query
- When presenting CV strengths/summaries, translate or paraphrase them to match the query language

Keep your response concise, professional, and actionable (max 300 words per language).
"""
            
            response = self.chat_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR consultant specializing in candidate matching and recruitment. You can communicate fluently in both Vietnamese and English, adapting your language to match the user's query."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            recommendation = response.choices[0].message.content
            logger.info("Generated AI recommendation successfully")
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
        Complete workflow: Generate embedding, search, and create recommendation
        
        Args:
            query: User search query
            db: Database session
            limit: Number of results to return
            
        Returns:
            Dictionary with query, results, and AI recommendation
        """
        try:
            # Step 1: Generate embedding for query
            logger.info(f"Processing search query: {query[:100]}...")
            query_embedding = self.generate_embedding(query)
            
            # Step 2: Find similar CVs
            similar_cvs = self.find_similar_cvs(query_embedding, db, limit)
            
            if not similar_cvs:
                return {
                    "query": query,
                    "results": [],
                    "ai_recommendation": "No matching CVs found in the database. Please upload some CVs first."
                }
            
            # Step 2.5: Check if similarity scores are too low (< 30%)
            max_similarity = max(cv.get('similarity_score', 0) for cv in similar_cvs)
            if max_similarity < 0.3:
                # Generate a helpful message based on query language
                sorry_message = self._generate_low_similarity_message(query)
                return {
                    "query": query,
                    "results": [],
                    "ai_recommendation": sorry_message
                }
            
            # Step 3: Generate AI recommendation
            ai_recommendation = self.generate_ai_recommendation(query, similar_cvs)
            
            # Step 4: Format results
            formatted_results = []
            for cv in similar_cvs:
                # Create a preview of the CV text
                text_preview = cv.get('extracted_text', '')[:200]
                
                formatted_results.append({
                    "id": cv['id'],
                    "filename": cv['filename'],
                    "similarity_score": round(cv['similarity_score'], 4),
                    "text_preview": text_preview + "..." if len(cv.get('extracted_text', '')) > 200 else text_preview,
                    "summary_pros": cv.get('summary_pros', ''),
                    "upload_time": cv['upload_time'].isoformat() if cv.get('upload_time') else None
                })
            
            return {
                "query": query,
                "results": formatted_results,
                "ai_recommendation": ai_recommendation
            }
            
        except Exception as e:
            logger.error(f"Error in search and recommend workflow: {str(e)}")
            raise

