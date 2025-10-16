# Interview Practice Chatbot - Implementation Guide

## Overview
A new Interview Practice Chatbot has been added to the CV Analyzer application. This chatbot uses OpenAI's API to simulate realistic job interviews and provide feedback to users.

## Features Implemented

### Backend (FastAPI)

1. **New Service: `backend/services/chatbot.py`**
   - `InterviewChatbot` class with OpenAI integration
   - Uses the same system prompt from the CLI bot
   - Maintains conversation history (max 10 messages)
   - Configurable via environment variables
   - Support for both regular and streaming responses

2. **API Endpoints in `backend/main.py`**
   - `POST /chatbot` - Send a message and get a response
   - `GET /chatbot/health` - Check if chatbot is properly configured

3. **Schemas in `backend/schemas.py`**
   - `ChatMessage` - Message format (role, content)
   - `ChatRequest` - Request with message and conversation history
   - `ChatResponse` - Response with assistant's message and timestamp

### Frontend (React)

1. **New Tab: "Interview Practice"**
   - Added to navigation header
   - Icon: MessageCircle from lucide-react

2. **ChatbotTab Component in `frontend/src/App.jsx`**
   - Modern chat interface with message bubbles
   - User messages on the right (blue), bot messages on the left (white)
   - Quick start buttons for popular job roles:
     - Software Engineer
     - Data Analyst
     - Marketing Manager
     - Product Manager
   - Features:
     - Auto-scroll to latest messages
     - Loading indicator while bot is typing
     - Conversation history tracking
     - Clear chat button
     - Enter to send, Shift+Enter for new line
     - Timestamps on all messages
     - Error handling with user-friendly messages

3. **API Functions in `frontend/src/services/api.js`**
   - `sendChatMessage(message, conversationHistory)` - Send message to bot
   - `chatbotHealthCheck()` - Check bot configuration status

## Environment Configuration

Add these environment variables to your `.env` file:

```env
# Required
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://aiportalapi.stu-platform.live/jpe
OPENAI_MODEL=gpt-4o-mini

# Optional (with defaults)
CHATBOT_MAX_TOKENS=500
CHATBOT_TEMPERATURE=0.7
CHATBOT_MAX_HISTORY=10
```

## Bot Behavior (System Prompt)

The chatbot follows these rules:

1. **Interview Context**
   - Asks one question at a time for the specified job role
   - Maximum of 5 questions per session
   - Moves to summary after 5 questions

2. **User Interaction**
   - If answer is too short/incorrect: Provides encouragement and moves to next question
   - If answer is good: Analyzes response, identifies missing points, provides constructive feedback

3. **Interview Flow**
   - Maintains continuity across questions
   - After 5 questions: Summarizes strengths, weaknesses, and provides a score (0-10)

4. **Out-of-Scope Handling**
   - Politely reminds user to focus on interview questions
   - Suggests alternative ways to help

5. **Style & Tone**
   - Professional, supportive, and realistic
   - Responds in Vietnamese by default (unless English is requested)
   - Concise but insightful

## Usage Flow

1. User navigates to "Interview Practice" tab
2. User either:
   - Clicks one of the quick start buttons, OR
   - Types their desired job role
3. Bot starts asking interview questions
4. User answers each question
5. Bot provides feedback and asks next question
6. After 5 questions, bot provides final evaluation
7. User can clear chat and start a new interview session

## Technical Details

### Message Format
```javascript
{
  role: "user" | "assistant",
  content: "message text",
  timestamp: "ISO date string"
}
```

### API Request Example
```javascript
POST /chatbot
{
  "message": "Tôi muốn luyện phỏng vấn vị trí Software Engineer",
  "conversation_history": [
    { "role": "user", "content": "previous message" },
    { "role": "assistant", "content": "previous response" }
  ]
}
```

### API Response Example
```javascript
{
  "response": "Đây là câu hỏi của bạn. ...",
  "timestamp": "2025-10-12T10:30:00Z"
}
```

## UI Components

- **Header**: Gradient background with bot icon and title
- **Message Area**: Scrollable chat history with auto-scroll
- **Empty State**: Welcome message with quick start buttons
- **Message Bubbles**: Color-coded by role (user/assistant/error)
- **Input Area**: Multi-line textarea with send button
- **Loading States**: Typing indicator with animated dots

## Error Handling

- Network errors show user-friendly Vietnamese error messages
- Failed requests add error message to chat
- Disabled send button during loading
- Form validation prevents empty messages

## Styling

- Uses Tailwind CSS classes
- Consistent with existing app design
- Responsive layout
- Smooth animations and transitions
- Accessible color contrast

## Testing

To test the chatbot:

1. Ensure `OPENAI_API_KEY` is set in backend `.env`
2. Start the backend: `cd backend && uvicorn main:app --reload`
3. Start the frontend: `cd frontend && npm run dev`
4. Navigate to "Interview Practice" tab
5. Click a quick start button or type a job role
6. Test the conversation flow

## Files Modified

### Backend
- `backend/services/chatbot.py` (new)
- `backend/main.py` (added chatbot endpoints)
- `backend/schemas.py` (added chatbot schemas)

### Frontend
- `frontend/src/App.jsx` (added chatbot tab and component)
- `frontend/src/services/api.js` (added chatbot API functions)

## Future Enhancements

Potential improvements:
- Save interview sessions to database
- Generate PDF reports of interview performance
- Add voice input/output
- Support for multiple languages
- Interview history and progress tracking
- Custom interview templates
- Real-time streaming responses

