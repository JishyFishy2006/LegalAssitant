"""Speech-to-Text endpoints."""

import os
import subprocess
import tempfile
import traceback
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from ..deps import get_app_components

router = APIRouter(prefix="/stt", tags=["Speech-to-Text"])


class TranscriptionResponse(BaseModel):
    transcript: str
    confidence: float
    language: str
    duration: float
    segments: List[Dict[str, Any]]
    error: Optional[str] = None


def convert_audio(input_bytes: bytes, input_format: str) -> bytes:
    """Convert audio to 16kHz mono WAV format using ffmpeg."""
    try:
        with tempfile.NamedTemporaryFile(suffix=f".{input_format}", delete=False) as input_file, \
             tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
            
            try:
                # Write input file
                input_file.write(input_bytes)
                input_file.flush()
                
                # Convert using ffmpeg
                cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite output file if it exists
                    '-i', input_file.name,  # Input file
                    '-ar', '16000',  # Sample rate
                    '-ac', '1',      # Mono channel
                    '-c:a', 'pcm_s16le',  # 16-bit PCM WAV
                    '-loglevel', 'error',  # Only show errors
                    output_file.name
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Read converted file
                with open(output_file.name, 'rb') as f:
                    return f.read()
                    
            finally:
                # Clean up temporary files
                try:
                    os.unlink(input_file.name)
                    os.unlink(output_file.name)
                except:
                    pass
                
    except Exception as e:
        print(f"Audio conversion failed: {e}")
        raise HTTPException(status_code=400, detail=f"Audio conversion failed: {str(e)}")


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(audio_file: UploadFile = File(...), app_components: Dict = Depends(get_app_components)):
    """
    Transcribe audio to text without processing it through the full pipeline.
    Returns the raw transcription with timing information.
    
    Supports: WAV, MP3, M4A, OGG, WEBM
    Converts to: 16kHz mono WAV
    """
    try:
        # Get STT component
        stt = app_components["stt"]
        if not stt:
            raise HTTPException(status_code=503, detail="Speech-to-text service not available")
        
        # Read audio file
        print(f"Received audio file: {audio_file.filename} ({audio_file.content_type}, {audio_file.size} bytes)")
        audio_bytes = await audio_file.read()
        
        # Convert to WAV if needed
        content_type = audio_file.content_type or "audio/wav"
        if content_type != "audio/wav":
            print(f"Converting {content_type} to WAV format...")
            audio_bytes = convert_audio(audio_bytes, content_type.split('/')[-1])
        
        # Process audio
        stt_result = stt.process(audio_bytes, mime_type="audio/wav")
        
        if "error" in stt_result:
            return TranscriptionResponse(
                transcript="",
                confidence=0.0,
                language="",
                duration=0.0,
                segments=[],
                error=stt_result["error"]
            )
            
        print(f"Transcription successful: {len(stt_result.get('transcript', ''))} chars")
        return TranscriptionResponse(**stt_result)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return TranscriptionResponse(
            transcript="",
            confidence=0.0,
            language="",
            duration=0.0,
            segments=[],
            error=error_msg
        )
