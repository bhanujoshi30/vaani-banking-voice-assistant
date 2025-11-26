"""
FastAPI application for AI backend
Handles chat requests and TTS generation
"""
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64

# Add backend to path for database access
# Handle both local development and Vercel deployment paths
# In Build Output API: python/ai/main.py -> python/backend/
# In local dev: ai/main.py -> backend/
backend_paths = [
    Path(__file__).parent.parent / "backend",  # python/backend/ (Build Output API)
    Path(__file__).parent.parent.parent / "backend",  # backend/ (local dev, if ai/ is deeper)
]

backend_path = None
for path in backend_paths:
    if path.exists() and (path / "db").exists():
        backend_path = path
        sys.path.insert(0, str(backend_path))
        break

# If backend not found, that's OK - backend is deployed separately on Vercel
if backend_path is None:
    import logging
    logging.warning("Backend path not found - backend features will be unavailable (expected for separate backend deployment)")

from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
import uvicorn

from config import settings
from services import get_llm_service, get_web_tts_service, get_guardrail_service, GuardrailViolationType
from agents.agent_graph import process_message
from utils import logger
from utils.demo_logging import demo_logger


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
    upi_mode: Optional[bool] = Field(default=None, description="Whether UPI mode is active (from frontend state)")


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


class VoiceVerificationRequest(BaseModel):
    """Request for AI-enhanced voice verification"""
    similarity_score: float = Field(..., description="Cosine similarity score from base verifier")
    threshold: float = Field(..., description="Base threshold value")
    user_context: Dict[str, Any] = Field(default_factory=dict, description="User context for analysis")
    analysis_prompt: Optional[str] = Field(default=None, description="Optional custom analysis prompt")


class QRCodeProcessRequest(BaseModel):
    """Request for QR code processing"""
    image_base64: str = Field(..., description="Base64 encoded image of QR code")
    language: str = Field(default="en-IN", description="Language code")


class QRCodeProcessResponse(BaseModel):
    """Response from QR code processing"""
    success: bool
    upi_address: Optional[str] = None
    amount: Optional[float] = None
    merchant_name: Optional[str] = None
    message: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    ollama_status: bool
    web_tts_available: bool


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered banking assistant backend",
)

def _build_allowed_origins() -> List[str]:
    """Return allowed CORS origins, including optional env overrides."""

    default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://*.vercel.app",
        "https://vaani-banking-voice-assistant-*.vercel.app",
        "https://sunnationalbank.online",
        "https://www.sunnationalbank.online",
    ]

    extra_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if extra_origins:
        default_origins.extend(
            origin.strip()
            for origin in extra_origins.split(",")
            if origin.strip()
        )

    seen = set()
    merged: List[str] = []
    for origin in default_origins:
        if origin not in seen:
            merged.append(origin)
            seen.add(origin)
    return merged


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_allowed_origins(),
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
    
    llm_healthy = await llm.health_check()
    
    # Check Web TTS availability (handle if not imported)
    web_tts_available = False
    if get_web_tts_service is not None:
        try:
            web_tts = get_web_tts_service()
            web_tts_available = web_tts.is_available()
        except Exception:
            pass
    
    return HealthResponse(
        status="healthy" if llm_healthy else "degraded",
        version=settings.app_version,
        ollama_status=llm_healthy,  # Keep field name for backward compatibility
        web_tts_available=web_tts_available
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
        # Demo logging: User message received
        demo_logger.chat_request(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message,
            language=request.language,
            voice_mode=request.voice_mode,
            upi_mode=request.upi_mode,
        )
        
        # State transition: User speaking -> Processing
        demo_logger.state_transition(
            from_state="USER SPEAKING",
            to_state="PROCESSING",
            reason="Message received, routing to agent"
        )
        
        logger.info(
            "chat_request",
            user_id=request.user_id,
            session_id=request.session_id,
            language=request.language,
            voice_mode=request.voice_mode,
            upi_mode=request.upi_mode  # Log UPI mode from request
        )
        
        # Input Guardrails: Check user input before processing
        guardrail_service = get_guardrail_service()
        input_check = await guardrail_service.check_input(
                language=request.language,
                timestamp=datetime.now().isoformat()
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
            message_history=history,
            upi_mode=request.upi_mode  # Pass UPI mode from frontend
        )
        
        # Output Guardrails: Check AI response before sending
        # Pass intent to allow guardrail to skip language check for language_change
        output_check = await guardrail_service.check_output(
            response=result.get("response", ""),
            language=result.get("language", request.language),  # Use updated language from result
            original_query=request.message,
            intent=result.get("intent")  # Pass intent to skip language check for language_change
        )
        
        if not output_check.passed:
            # Log guardrail violation
            logger.warning(
                "guardrail_violation_output",
                user_id=request.user_id,
                violation_type=output_check.violation_type,
                language=request.language,
                response_preview=result.get("response", "")[:100]
            )
            
            # Replace with safe fallback message
            if request.language == "hi-IN":
                fallback_message = "मुझे खेद है, मुझे आपकी मदद करने में समस्या हो रही है। कृपया पुनः प्रयास करें।"
            else:
                fallback_message = "I'm sorry, I'm having trouble helping you right now. Please try again."
            
            result["response"] = fallback_message
        
        # Demo logging: AI response
        demo_logger.ai_response(
            response=result.get("response", ""),
            agent=result.get("intent", "unknown"),
            language=request.language,
        )
        
        # State transition: Processing -> AI speaking
        demo_logger.state_transition(
            from_state="PROCESSING",
            to_state="AI SPEAKING",
            reason="Response generated, sending to user"
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error("chat_endpoint_error", error=str(e))
        demo_logger.error("Chat endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qr-code/process", response_model=QRCodeProcessResponse)
async def process_qr_code(request: QRCodeProcessRequest):
    """
    Process QR code image to extract UPI payment details
    
    Uses AI service to extract UPI address and payment details from QR code image
    """
    try:
        import io
        from PIL import Image
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image_base64.split(',')[-1])
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            logger.error("qr_decode_error", error=str(e))
            return QRCodeProcessResponse(
                success=False,
                message="Failed to decode image" if request.language != "hi-IN" else "छवि डिकोड करने में विफल",
                error=str(e)
            )
        
        # Try to decode QR code using pyzbar or jsQR (via frontend)
        try:
            # Try pyzbar first (backend library)
            try:
                from pyzbar.pyzbar import decode
                decoded_objects = decode(image)
            except ImportError:
                # pyzbar not available, try using jsQR via frontend or AI service
                decoded_objects = []
            
            if not decoded_objects:
                # If pyzbar fails, try using AI service to extract UPI details
                llm = get_llm_service()
                
                # Convert image to base64 for AI processing
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Use AI to extract UPI details from QR code
                prompt = f"""Analyze this QR code image and extract UPI payment details.

The image is provided as base64. Extract:
- UPI address (format: username@payee)
- Amount (if present)
- Merchant name (if present)

Return JSON with:
{{
  "upi_address": "upi_address_or_null",
  "amount": amount_or_null,
  "merchant_name": "merchant_name_or_null"
}}

Return ONLY valid JSON, nothing else."""

                # For now, return a message asking user to provide details
                # In production, you would use vision-capable models
                return QRCodeProcessResponse(
                    success=False,
                    message="QR code scanning requires vision model. Please enter UPI details manually." if request.language != "hi-IN" else "QR कोड स्कैनिंग के लिए विज़न मॉडल की आवश्यकता है। कृपया UPI विवरण मैन्युअल रूप से दर्ज करें।",
                    error="Vision model not configured"
                )
            
            # Extract data from QR code
            qr_data = decoded_objects[0].data.decode('utf-8')
            
            # Parse UPI QR code format
            # UPI QR codes typically contain: upi://pay?pa=<upi_id>&pn=<name>&am=<amount>&cu=INR
            upi_address = None
            amount = None
            merchant_name = None
            
            if 'upi://' in qr_data or 'UPI://' in qr_data:
                # Parse UPI QR code
                import urllib.parse
                parsed = urllib.parse.urlparse(qr_data)
                params = urllib.parse.parse_qs(parsed.query)
                
                upi_address = params.get('pa', [None])[0]
                merchant_name = params.get('pn', [None])[0]
                amount_str = params.get('am', [None])[0]
                
                if amount_str:
                    try:
                        amount = float(amount_str)
                    except:
                        amount = None
            
            if not upi_address:
                # Try to extract UPI ID from QR data directly
                if '@' in qr_data:
                    # Look for UPI ID pattern
                    import re
                    upi_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)', qr_data)
                    if upi_match:
                        upi_address = upi_match.group(1)
            
            if upi_address:
                return QRCodeProcessResponse(
                    success=True,
                    upi_address=upi_address,
                    amount=amount,
                    merchant_name=merchant_name,
                    message="QR code processed successfully" if request.language != "hi-IN" else "QR कोड सफलतापूर्वक संसाधित"
                )
            else:
                return QRCodeProcessResponse(
                    success=False,
                    message="Could not extract UPI address from QR code" if request.language != "hi-IN" else "QR कोड से UPI पता निकाला नहीं जा सका",
                    error="No UPI address found"
                )
                
        except ImportError:
            # pyzbar not available, use AI service
            logger.warning("pyzbar_not_available", message="Using AI service for QR code processing")
            
            # Use AI service to process QR code
            llm = get_llm_service()
            
            # For now, return error asking to install pyzbar or use manual entry
            return QRCodeProcessResponse(
                success=False,
                message="QR code library not available. Please enter UPI details manually." if request.language != "hi-IN" else "QR कोड लाइब्रेरी उपलब्ध नहीं है। कृपया UPI विवरण मैन्युअल रूप से दर्ज करें।",
                error="QR code library not installed"
            )
        except Exception as e:
            logger.error("qr_processing_error", error=str(e))
            return QRCodeProcessResponse(
                success=False,
                message=f"Failed to process QR code: {str(e)}" if request.language != "hi-IN" else f"QR कोड प्रसंस्करण विफल: {str(e)}",
                error=str(e)
            )
            
    except Exception as e:
        logger.error("qr_endpoint_error", error=str(e))
        return QRCodeProcessResponse(
            success=False,
            message=f"Error processing QR code: {str(e)}" if request.language != "hi-IN" else f"QR कोड प्रसंस्करण में त्रुटि: {str(e)}",
            error=str(e)
        )


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
    Convert text to speech using Web TTS (gTTS)
    
    Uses Google Text-to-Speech API - free, no API keys needed
    Supports Hindi and English with Indian accents
    """
    try:
        if get_web_tts_service is None:
            raise HTTPException(
                status_code=503,
                detail="Web TTS not available. gTTS package not installed."
            )
        
        web_tts = get_web_tts_service()
        
        if not web_tts.is_available():
            raise HTTPException(
                status_code=503,
                detail="Web TTS not available"
            )
        
        logger.info(
            "tts_request",
            text_length=len(request.text),
            language=request.language
        )
        
        # Synthesize speech using gTTS
        audio_data = await web_tts.synthesize_text(
            text=request.text,
            language=request.language
        )
        
        # Return audio as response (gTTS returns MP3 format)
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("tts_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice-verification")
async def voice_verification(request: VoiceVerificationRequest):
    """
    AI-enhanced voice verification endpoint
    
    Uses LLM to analyze voice verification context and provide enhanced decision
    """
    try:
        from services.ai_voice_verification import AIVoiceVerificationService
        
        service = AIVoiceVerificationService()
        result = await service.analyze_verification(
            similarity_score=request.similarity_score,
            threshold=request.threshold,
            user_context=request.user_context,
            analysis_prompt=request.analysis_prompt
        )
        
        return {
            "success": result.accept,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "fallback_to_basic": result.fallback_to_basic
        }
        
    except Exception as e:
        logger.error("voice_verification_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Export app for Vercel
# Vercel will use this app object directly
__all__ = ["app"]


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info"
    )
