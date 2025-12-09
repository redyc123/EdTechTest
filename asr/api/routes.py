from fastapi import APIRouter
from api.models import *
import secrets
import os
from datetime import datetime, timedelta
from fastapi import File, UploadFile, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import tempfile


from constants import MODEL, SECRET_TOKEN

auth_router = APIRouter(tags=["AUTH"])
asr_router = APIRouter(tags=["ASR"])
valid_tokens = []

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    """Get current user by checking the token in Authorization header or query parameter"""
    token = None

    # Check authorization header
    if credentials:
        token = credentials.credentials
    else:
        # Check query parameter (for cases where header isn't accessible)
        token = None  # Will be retrieved from request later

    return token

def verify_token(token: str) -> bool:
    """Check if the token is valid and not expired"""
    global valid_tokens
    # Remove expired tokens
    current_time = datetime.utcnow()
    valid_tokens = [t for t in valid_tokens if t.expires_at > current_time]

    # Check if the token exists in valid_tokens
    for token_data in valid_tokens:
        if token_data.token == token:
            return True
    return False

def require_valid_token(request: Request, token: str = Depends(get_current_user)):
    """Dependency that checks for a valid token in header or query param"""
    # If token is not in header, check query parameter
    if not token:
        token = request.query_params.get('token', "")

    if not token or not verify_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@auth_router.post("/generate-token")
async def generate_token(request: GenerateTokenRequest):
    """
    Generate a new access token using the secret token.
    The secret token should be passed in the request body.
    """
    if request.secret_token != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid secret token")
    
    # Generate a new token
    access_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    
    # Store the token
    token_data = TokenData(token=access_token, expires_at=expires_at)
    valid_tokens.append(token_data)
    
    return GenerateTokenResponse(
        access_token=access_token,
        expires_at=expires_at.isoformat()
    )


@asr_router.post("/transcribe", response_model=TranscriptionResponse, dependencies=[Depends(require_valid_token)])
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file to text using Whisper.
    
    Supported audio formats: mp3, wav, m4a, mp4, mpga, m4v, avi, mov, flv, mkv, webm
    """
    if not file.filename:
        raise Exception("FILENAME NOT FOUND")
    # Check if the uploaded file is an audio file
    content_type = file.content_type
    if not content_type or not content_type.startswith("audio/"):
        # Allow some video formats that contain audio
        allowed_extensions = [".mp3", ".wav", ".m4a", ".mp4", ".mpga", ".m4v", ".avi", ".mov", ".flv", ".mkv", ".webm"]
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="File must be an audio or video file")
    
    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        try:
            # Save the uploaded file to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            
            # Transcribe the audio using Whisper
            result = MODEL.transcribe(temp_file_path)
            
            # Extract transcription details
            if not isinstance(result, dict):
                raise Exception("RESULT NOT DICT")
            transcription_text = result["text"].strip() # type: ignore
            detected_language = result.get("language", None)
            
            # Calculate duration
            duration = None
            if "segments" in result and len(result["segments"]) > 0:
                last_segment = result["segments"][-1]
                duration = last_segment["end"] if "end" in last_segment else None
            
            return TranscriptionResponse(
                text=transcription_text,
                language=detected_language,
                duration=duration
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing audio file: {str(e)}")
        
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass  # Ignore errors during cleanup


@asr_router.get("/health", response_model=HealthCheck, dependencies=[Depends(require_valid_token)])
async def health_check():
    """Health check endpoint to verify the service is running."""
    return HealthCheck(status="OK")