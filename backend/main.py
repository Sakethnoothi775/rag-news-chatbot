from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
import uuid
from datetime import datetime
import logging

from config import Config
from rag_pipeline_simple import RAGPipeline
from session_manager import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG News Chatbot API",
    description="A RAG-powered chatbot for news websites",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
config = Config()
rag_pipeline = RAGPipeline()
session_manager = SessionManager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict]
    confidence: float
    session_id: str
    timestamp: str

class SessionResponse(BaseModel):
    session_id: str
    created_at: str

class SessionHistory(BaseModel):
    session_id: str
    messages: List[Dict]
    created_at: str
    last_activity: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup"""
    try:
        logger.info("Starting RAG News Chatbot API...")
        
        # Load and index articles
        success = await rag_pipeline.load_and_index_articles()
        if success:
            logger.info("RAG pipeline initialized successfully")
        else:
            logger.warning("Failed to initialize RAG pipeline - some features may not work")
            
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "RAG News Chatbot API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Process chat message and return response"""
    try:
        # Generate or use existing session ID
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Store user message in session
        await session_manager.add_message(
            session_id, 
            "user", 
            chat_message.message
        )
        
        # Process query through RAG pipeline
        result = await rag_pipeline.query(chat_message.message)
        
        # Store bot response in session
        await session_manager.add_message(
            session_id, 
            "assistant", 
            result['answer']
        )
        
        return ChatResponse(
            answer=result['answer'],
            sources=result['sources'],
            confidence=result['confidence'],
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        await session_manager.create_session(session_id)
        
        return SessionResponse(
            session_id=session_id,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/history", response_model=SessionHistory)
async def get_session_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = await session_manager.get_session_history(session_id)
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionHistory(**history)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear chat history for a session"""
    try:
        success = await session_manager.clear_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    try:
        sessions = await session_manager.list_sessions()
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message through RAG pipeline
            result = await rag_pipeline.query(message_data['message'])
            
            # Store messages in session
            await session_manager.add_message(session_id, "user", message_data['message'])
            await session_manager.add_message(session_id, "assistant", result['answer'])
            
            # Send response back to client
            response = {
                "type": "message",
                "data": {
                    "answer": result['answer'],
                    "sources": result['sources'],
                    "confidence": result['confidence'],
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for session {session_id}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check RAG pipeline status
        rag_status = "healthy" if rag_pipeline.gemini_model else "degraded"
        
        # Check session manager status
        session_status = "healthy" if session_manager.redis_client else "degraded"
        
        return {
            "status": "healthy" if rag_status == "healthy" and session_status == "healthy" else "degraded",
            "components": {
                "rag_pipeline": rag_status,
                "session_manager": session_status,
                "vector_store": "healthy" if rag_pipeline.qdrant_client else "unavailable"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )

