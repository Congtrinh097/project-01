import os
import logging
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from .bot_tools import (
    get_total_jobs_count,
    get_jobs_summary_by_technical_skills,
)

logger = logging.getLogger(__name__)

class MainBot:
    """
    Main Bot with RAG (Retrieval-Augmented Generation) using Local FAISS + Tavily
    """
    
    SYSTEM_PROMPT = """You are a helpful and knowledgeable assistant. 
    Use the available tools to search for information when needed.
    Provide clear, accurate, and helpful responses to user questions.
    If you use tools to gather information, synthesize the results into a coherent answer.
    Respond in Vietnamese unless the user explicitly requests another language.
    
    This will make your responses more visually appealing and easier to read."""
    
    def __init__(self):
        """Initialize the Main Bot with FAISS vector store and Tavily search"""
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("MAIN_BOT_TEMPERATURE", "0.3"))
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
            self.embedding_model = None
            self.db = None
            self.retriever = None
            self.graph = None
        else:
            try:
                # Initialize OpenAI client
                if self.base_url:
                    logger.info(f"Using custom OpenAI base URL: {self.base_url}")
                    self.client = ChatOpenAI(
                        model=self.model_name,
                        temperature=self.temperature,
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                else:
                    logger.info("Using standard OpenAI API endpoint")
                    self.client = ChatOpenAI(
                        model=self.model_name,
                        temperature=self.temperature,
                        api_key=self.api_key
                    )
                
                # Initialize embedding model
                if self.base_url:
                    self.embedding_model = OpenAIEmbeddings(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                else:
                    self.embedding_model = OpenAIEmbeddings(api_key=self.api_key)
                
                # Initialize knowledge base with mock chunks (can be extended with real data)
                self._initialize_knowledge_base()
                
                # Initialize tools
                self._initialize_tools()
                
                # Build LangGraph
                self._build_graph()
                
                logger.info("Main Bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Main Bot: {e}")
                self.client = None
                self.embedding_model = None
                self.db = None
                self.retriever = None
                self.graph = None
    
    def _initialize_knowledge_base(self):
        """Initialize FAISS vector store with knowledge base chunks"""
        # Mock knowledge base chunks (can be extended with real data)
        mock_chunks = [
            Document(page_content="CV Analyzer helps you analyze resumes and find the best candidates for job positions."),
            Document(page_content="You can upload CV files in PDF or DOCX format for analysis."),
            Document(page_content="The system uses AI to analyze CV strengths and weaknesses, providing detailed feedback."),
            Document(page_content="Job recommendations are based on semantic similarity matching using vector embeddings."),
            Document(page_content="You can practice interview skills with the Interview Practice Bot."),
            Document(page_content="The system supports Vietnamese and English languages."),
            Document(page_content="CV recommendations use cosine similarity to find the most relevant candidates."),
            Document(page_content="You can generate professional resumes from text input using AI."),
        ]
        
        try:
            self.db = FAISS.from_documents(mock_chunks, self.embedding_model)
            self.retriever = self.db.as_retriever()
            logger.info("Knowledge base initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            self.db = None
            self.retriever = None
    
    def _initialize_tools(self):
        """Initialize tools for the bot"""
        # Tool for retrieving internal knowledge
        @tool
        def retrieve_advice(user_input: str) -> str:
            """Searches internal knowledge base for relevant information."""
            if not self.retriever:
                return "Knowledge base not available."
            try:
                docs = self.retriever.get_relevant_documents(user_input)
                if not docs:
                    return "No relevant information found in internal database."
                return "\n".join(doc.page_content for doc in docs)
            except Exception as e:
                logger.error(f"Error retrieving from knowledge base: {e}")
                return f"Error searching knowledge base: {str(e)}"
        
        # Tavily search tool (requires TAVILY_API_KEY)
        tavily_api_key = settings.TAVILY_API_KEY
        if tavily_api_key:
            try:
                self.tavily_tool = TavilySearchResults(max_results=3, api_key=tavily_api_key)
                logger.info("Tavily search tool initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily tool: {e}")
                self.tavily_tool = None
        else:
            logger.warning("TAVILY_API_KEY not found, Tavily search disabled")
            self.tavily_tool = None
        
        # Store tools
        self.retrieve_advice_tool = retrieve_advice
        self.get_total_jobs_count_tool = get_total_jobs_count
        self.get_jobs_summary_by_technical_skills_tool = get_jobs_summary_by_technical_skills
        
        # Tools list for LLM
        tools = [
            retrieve_advice,
            get_total_jobs_count,
            get_jobs_summary_by_technical_skills,
        ]
        if self.tavily_tool:
            tools.append(self.tavily_tool)
        
        self.tools = tools
    
    def _build_graph(self):
        """Build the LangGraph for tool calling"""
        if not self.client or not self.tools:
            return
        
        try:
            # Bind tools to LLM
            llm_with_tools = self.client.bind_tools(self.tools)
            
            # Define nodes
            def call_model(state: MessagesState):
                messages = state["messages"]
                response = llm_with_tools.invoke(messages)
                return {"messages": [response]}
            
            def should_continue(state: MessagesState):
                last_message = state["messages"][-1]
                if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                    return "tools"
                return END
            
            tool_node = ToolNode(self.tools)
            
            # Build graph
            graph_builder = StateGraph(MessagesState)
            graph_builder.add_node("call_model", call_model)
            graph_builder.add_node("tools", tool_node)
            
            graph_builder.add_edge(START, "call_model")
            graph_builder.add_conditional_edges("call_model", should_continue, ["tools", END])
            graph_builder.add_edge("tools", "call_model")
            
            self.graph = graph_builder.compile()
            logger.info("LangGraph built successfully")
        except Exception as e:
            logger.error(f"Failed to build graph: {e}")
            self.graph = None
    
    def get_response(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Get a response from the Main Bot using RAG
        
        Args:
            user_input: The user's message
            conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            The assistant's response text
        """
        if not self.graph:
            return "⚠️ Main Bot is not available. Please check your API key configuration."
        
        try:
            # Build messages
            messages = []
            
            # Add system message
            messages.append(SystemMessage(content=self.SYSTEM_PROMPT))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Limit to last 10 messages
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append({
                            "role": "assistant",
                            "content": content
                        })
            
            # Add current user input
            messages.append(HumanMessage(content=user_input))
            
            # Invoke graph
            logger.info(f"Processing Main Bot request: {user_input[:50]}...")
            result = self.graph.invoke({"messages": messages})
            
            # Get the last assistant message
            last_message = result["messages"][-1]
            
            # Extract content from the message
            if hasattr(last_message, "content"):
                response_text = last_message.content
            else:
                response_text = str(last_message)
            
            logger.info(f"Main Bot response generated: {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting Main Bot response: {str(e)}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn: {str(e)}"

