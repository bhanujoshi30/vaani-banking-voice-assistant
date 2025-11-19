"""
FastAPI application for AI backend
Handles chat requests and TTS generation
"""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add backend to path for database access
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
import uvicorn

from config import settings
from services import get_llm_service, get_azure_tts_service
from agents.agent_graph import process_message
from utils import logger


# Pydantic models for API
class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat completion"""
    model_config = ConfigDict(populate_by_name=True)
    
    message: str = Field(..., description="User's message")
    user_id: Optional[str] = Field(default=None, description="User ID (UUID string)")
    session_id: str = Field(..., description="Session ID")
    language: str = Field(default="en-IN", description="Language code")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="User context")
    message_history: Optional[List[ChatMessage]] = Field(default=None, description="Conversation history")
    voice_mode: bool = Field(default=False, description="Whether in voice mode (use fast model)")


class ChatResponse(BaseModel):
    """Response from chat completion"""
    success: bool
    response: str
    intent: Optional[str] = None
    language: str
    timestamp: str
    statement_data: Optional[Dict[str, Any]] = None  # Account statement data for download
    structured_data: Optional[Dict[str, Any]] = None  # Structured data for UI components


class TTSRequest(BaseModel):
    """Request for text-to-speech"""
    text: str = Field(..., description="Text to synthesize")
    language: str = Field(default="en-IN", description="Language code")
    use_azure: bool = Field(default=False, description="Use Azure TTS if available")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    ollama_status: bool
    azure_tts_available: bool


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered banking assistant backend",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors for debugging"""
    logger.error("validation_error", errors=exc.errors(), body=exc.body)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    logger.info(
        "request_received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown"
    )
    
    response = await call_next(request)
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_seconds=duration
    )
    
    return response


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    llm = get_llm_service()
    azure_tts = get_azure_tts_service()
    
    llm_healthy = await llm.health_check()
    
    return HealthResponse(
        status="healthy" if llm_healthy else "degraded",
        version=settings.app_version,
        ollama_status=llm_healthy,  # Keep field name for backward compatibility
        azure_tts_available=azure_tts.is_available()
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through the agent system
    
    This endpoint:
    1. Classifies user intent
    2. Routes to appropriate agent
    3. Executes banking tools if needed
    4. Returns AI-generated response
    """
    try:
        logger.info(
            "chat_request",
            user_id=request.user_id,
            session_id=request.session_id,
            language=request.language,
            voice_mode=request.voice_mode
        )
        
        # Convert message history
        history = []
        if request.message_history:
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.message_history
            ]
        
        # Process through agent graph
        result = await process_message(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            language=request.language,
            user_context=request.user_context,
            message_history=history
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response for real-time updates
    
    Returns Server-Sent Events (SSE) stream
    """
    try:
        logger.info(
            "chat_stream_request",
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        async def generate():
            """Generate streaming response"""
            llm = get_llm_service()
            
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": f"You are Vaani, a banking assistant. Respond in {request.language}."
                }
            ]
            
            if request.message_history:
                for msg in request.message_history:
                    messages.append({"role": msg.role, "content": msg.content})
            
            messages.append({"role": "user", "content": request.message})
            
            # Stream response
            async for chunk in llm.chat_stream(
                messages,
                use_fast_model=request.voice_mode
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error("chat_stream_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Azure TTS
    
    Falls back to error message if Azure TTS not available
    """
    try:
        azure_tts = get_azure_tts_service()
        
        if not azure_tts.is_available() or not request.use_azure:
            raise HTTPException(
                status_code=503,
                detail="Azure TTS not available. Use Web Speech API on frontend."
            )
        
        logger.info(
            "tts_request",
            text_length=len(request.text),
            language=request.language
        )
        
        # Synthesize speech
        audio_data = await azure_tts.synthesize_text(
            text=request.text,
            language=request.language
        )
        
        # Return audio as response
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("tts_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def list_models():
    """List available Ollama models"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            return response.json()
    except Exception as e:
        logger.error("list_models_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )
    
    # Check LLM connection
    llm = get_llm_service()
    provider_name = llm.get_provider_name()
    if await llm.health_check():
        logger.info("llm_connected", provider=provider_name, config=f"LLM_PROVIDER={settings.llm_provider}")
    else:
        logger.warning("llm_not_available", provider=provider_name)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("application_shutdown")
    
    # Close connections
    llm = get_llm_service()
    await llm.close()


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
