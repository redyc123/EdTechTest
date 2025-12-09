from fastapi import APIRouter
from api.models import *
import secrets
import os
from datetime import datetime, timedelta
from fastapi import File, UploadFile, HTTPException, Depends
import tempfile
from common.auth.auth import require_valid_token, valid_tokens


from constants import MODEL

asr_router = APIRouter(tags=["ASR"])


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
                if not isinstance(last_segment, dict):
                    raise Exception("LAST_SEGMENT NOT DICT")
                duration = last_segment["end"] if "end" in last_segment else None
            
            return TranscriptionResponse(
                text=transcription_text,
                language=detected_language if isinstance(detected_language, str) else None,
                duration=duration if isinstance(duration, float) else None
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