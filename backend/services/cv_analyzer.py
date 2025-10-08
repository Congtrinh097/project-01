import openai
import logging
from typing import Dict
from config import settings

logger = logging.getLogger(__name__)

class CVAnalyzer:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url="https://aiportalapi.stu-platform.live/jpe")
    
    async def analyze_cv(self, cv_text: str) -> Dict[str, str]:
        """
        Analyze CV text using OpenAI GPT-4o-mini
        Returns dictionary with 'pros' and 'cons' keys
        """
        try:
            prompt = self._create_analysis_prompt(cv_text)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR professional and career counselor. Analyze CVs objectively and provide constructive feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the response to extract pros and cons
            pros, cons = self._parse_analysis_response(analysis_text)
            
            logger.info("CV analysis completed successfully")
            return {
                "pros": pros,
                "cons": cons
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CV: {str(e)}")
            raise ValueError(f"Failed to analyze CV: {str(e)}")
    
    def _create_analysis_prompt(self, cv_text: str) -> str:
        """
        Create a prompt for CV analysis
        """
        return f"""
Please analyze the following CV and provide a structured response with strengths (pros) and areas for improvement (cons).

CV Content:
{cv_text[:4000]}  # Limit to avoid token limits

Please format your response exactly as follows:

STRENGTHS:
- [List key strengths and positive aspects]

AREAS FOR IMPROVEMENT:
- [List constructive suggestions and areas to develop]

Focus on:
- Skills and experience relevance
- Education and certifications
- Career progression
- Technical competencies
- Communication and presentation
- Overall structure and completeness

Be constructive and specific in your feedback.
"""
    
    def _parse_analysis_response(self, response_text: str) -> tuple[str, str]:
        """
        Parse the OpenAI response to extract pros and cons
        """
        try:
            lines = response_text.split('\n')
            pros_lines = []
            cons_lines = []
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.upper().startswith('STRENGTHS'):
                    current_section = 'pros'
                    continue
                elif line.upper().startswith(('AREAS FOR IMPROVEMENT', 'WEAKNESSES', 'CONS')):
                    current_section = 'cons'
                    continue
                elif line.startswith('-') and current_section:
                    if current_section == 'pros':
                        pros_lines.append(line[1:].strip())
                    elif current_section == 'cons':
                        cons_lines.append(line[1:].strip())
            
            pros = '\n'.join(pros_lines) if pros_lines else "No specific strengths identified."
            cons = '\n'.join(cons_lines) if cons_lines else "No specific areas for improvement identified."
            
            return pros, cons
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            # Return the full response as pros if parsing fails
            return response_text, "Error parsing detailed analysis."

