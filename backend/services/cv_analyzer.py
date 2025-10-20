import openai
import logging
from typing import Dict
from config import settings

logger = logging.getLogger(__name__)

class CVAnalyzer:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        # Use custom base_url if provided, otherwise use default OpenAI endpoint
        base_url = getattr(settings, 'OPENAI_BASE_URL', None)
        if base_url:
            logger.info(f"Using custom OpenAI base URL: {base_url}")
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url=base_url)
        else:
            logger.info("Using standard OpenAI API endpoint")
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
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
                        "content": "You are an expert HR professional and career counselor. Analyze CVs objectively and provide constructive feedback. You can communicate fluently in both Vietnamese and English."
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

LANGUAGE INSTRUCTIONS:
- If the CV content is primarily in Vietnamese, provide your analysis in Vietnamese,
- If the CV content is in English or any other language, respond only in English
- If the CV content is in both Vietnamese and English, respond in both languages
- If the CV content is in other languages, respond in the language of the CV content
- When presenting CV strengths/areas for improvement, translate or paraphrase them to match the CV content language


Please format your response exactly as follows using markdown formatting:

**Strengths:** (or **Điểm mạnh:** for Vietnamese)
- **Relevant Experience**: [Description of experience alignment]
- **Technical Proficiency**: [Description of technical skills]
- **Quantifiable Achievements**: [Description of measurable accomplishments]
- **Diverse Skill Set**: [Description of additional skills]
- **Project Experience**: [Description of relevant projects]
- **Recognition**: [Description of awards or recognition]

**Areas for Improvement:** (or **Điểm cần cải thiện:** for Vietnamese)
- **Education Section**: [Suggestions for education presentation]
- **Certifications**: [Recommendations for certifications]
- **Career Progression**: [Suggestions for career narrative]
- **Communication Skills**: [Recommendations for soft skills]
- **Formatting and Structure**: [Suggestions for CV layout]
- **Language Proficiency**: [Recommendations for language skills]

Focus on:
- Skills and experience relevance
- Education and certifications
- Career progression
- Technical competencies
- Communication and presentation
- Overall structure and completeness

Be constructive and specific in your feedback. Use markdown formatting with **bold** text for section headers and bullet points for detailed descriptions.
"""
    
    def _parse_analysis_response(self, response_text: str) -> tuple[str, str]:
        """
        Parse the OpenAI response to extract pros and cons with markdown formatting
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
                
                line_upper = line.upper().replace('*', '').replace(':', '')
                
                # Check for section headers - more flexible matching (English and Vietnamese)
                if any(keyword in line_upper for keyword in ['STRENGTH', 'PROS', 'ĐIỂM MẠNH', 'DIEM MANH']):
                    current_section = 'pros'
                    continue
                elif any(keyword in line_upper for keyword in ['IMPROVEMENT', 'WEAKNESS', 'CONS', 'AREAS FOR', 'ĐIỂM CẦN CẢI THIỆN', 'DIEM CAN CAI THIEN']):
                    current_section = 'cons'
                    continue
                elif line.startswith(('-', '•', '*')) and current_section:
                    # Keep the markdown formatting intact
                    if current_section == 'pros':
                        pros_lines.append(line)
                    elif current_section == 'cons':
                        cons_lines.append(line)
                elif current_section and line and not line.startswith('**') and not line.startswith('Focus on'):
                    # Handle content that's part of the current section but not bullet points
                    if current_section == 'pros':
                        pros_lines.append(f"- {line}")
                    elif current_section == 'cons':
                        cons_lines.append(f"- {line}")
            
            pros = '\n'.join(pros_lines) if pros_lines else "No specific strengths identified."
            cons = '\n'.join(cons_lines) if cons_lines else "No specific areas for improvement identified."
            
            return pros, cons
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {str(e)}")
            # Return the full response as pros if parsing fails
            return response_text, "Error parsing detailed analysis."

