import os
import logging
from typing import List, Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class InterviewChatbot:
    """
    Intelligent Recruitment Interview Practice Bot using OpenAI API
    """
    
    SYSTEM_PROMPT = """
You are an Intelligent Recruitment Interview Practice Bot.  
Your role is to simulate a realistic interview for users based on their chosen profession.  
Follow these rules strictly:

1. Interview Context
- When the user specifies a job role or industry, generate professional interview questions relevant to that role.  
- Ask one question at a time, just like a real interviewer.  
- The interview session has a maximum of 5 questions. After finishing, move to the summary step.  

2. User Interaction
- If the user answers:
   - If the answer is too short or incorrect → respond with:
     "Vui lòng cố gắng học thêm kiến thức để trả lời câu hỏi. Chúng ta sẽ chuyển sang câu tiếp theo."
   - Otherwise → analyze their response:
       - Identify missing points, unclear expressions, or weak parts.  
       - Provide constructive feedback and specific references (articles, frameworks, study topics) for improvement.  

3. Interview Flow
- Maintain continuity across questions, referring back to previous answers if relevant.  
- After 5 questions or when the interview ends:
   - Summarize strengths of the candidate.  
   - Summarize weaknesses of the candidate. 
   - Provide a final evaluation score (0–10).  

4. Out-of-Scope Handling
- If the user asks something unrelated to the interview, politely remind them:  
  "Xin lưu ý: bạn đang trong buổi phỏng vấn giả định. Vui lòng tập trung vào câu hỏi." 
- If the user asks something unrelated to the interview, politely remind them: 
    Suggest another way to help them.

5. Style & Tone
- Be professional, supportive, and realistic.  
- Respond in Vietnamese unless the user explicitly requests English.  
- Keep answers concise but insightful.  

6. Before output.
- Before output, you need to say "Đây là câu hỏi của bạn."

7. After user anwser.
- You need to say "Cảm ơn câu trả lời của bạn."


Your goal: Help the user improve their interview skills by providing realistic practice, immediate feedback, and actionable learning resources.
"""
    
    def __init__(self):
        """Initialize the chatbot with OpenAI client"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://aiportalapi.stu-platform.live/jpe")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("CHATBOT_MAX_TOKENS", "500"))
        self.temperature = float(os.getenv("CHATBOT_TEMPERATURE", "0.7"))
        self.max_history_items = int(os.getenv("CHATBOT_MAX_HISTORY", "10"))
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def _build_messages(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build messages array for OpenAI API with conversation history"""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        # Add conversation history if provided (limit to max_history_items)
        if conversation_history:
            limited_history = conversation_history[-self.max_history_items:]
            messages.extend(limited_history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def get_response(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Get a response from the chatbot based on user input and conversation history
        
        Args:
            user_input: The user's message
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            The assistant's response text
        """
        if not self.client:
            return "⚠️ OpenAI client is not available. Please check your API key configuration."
        
        try:
            messages = self._build_messages(user_input, conversation_history)
            
            logger.info(f"Sending request to OpenAI with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            
            assistant_message = response.choices[0].message.content
            logger.info(f"Received response from OpenAI: {len(assistant_message)} characters")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error getting chatbot response: {str(e)}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn: {str(e)}"
    
    async def get_response_stream(
        self, 
        user_input: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """
        Get a streaming response from the chatbot
        
        Args:
            user_input: The user's message
            conversation_history: List of previous messages
        
        Yields:
            Chunks of the assistant's response
        """
        if not self.client:
            yield "⚠️ OpenAI client is not available. Please check your API key configuration."
            return
        
        try:
            messages = self._build_messages(user_input, conversation_history)
            
            logger.info(f"Sending streaming request to OpenAI with {len(messages)} messages")
            
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            yield f"\n\nXin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn: {str(e)}"

