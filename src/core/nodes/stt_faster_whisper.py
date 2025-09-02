"""Speech-to-Text node using Faster Whisper."""
import os
import tempfile
import traceback
from typing import Dict, Any, Optional, List
from faster_whisper import WhisperModel

class STTNode:
    """Speech-to-Text node for converting audio to text using Faster Whisper."""
    
    def __init__(self, model_size: str = "tiny.en"):
        """Initialize STT node with Faster Whisper model.
        
        Args:
            model_size: Size of the Whisper model (tiny.en, base.en, small.en, etc.)
        """
        try:
            self.model_size = model_size
            self.model = WhisperModel(
                model_size_or_path=model_size,
                device="cpu",
                compute_type="int8",
                download_root="./models/whisper"
            )
            print(f"✓ Loaded Whisper model: {model_size}")
        except Exception as e:
            print(f"Failed to initialize Whisper model: {e}")
            traceback.print_exc()
            raise
    
    def process(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> Dict[str, Any]:
        """
        Convert audio bytes to transcript text using Faster Whisper.
        
        Args:
            audio_bytes: Raw audio data
            mime_type: Audio format (audio/wav, audio/mp3, etc.)
            
        Returns:
            Dict with transcript and timing information
        """
        import time
        start_time = time.time()
        temp_path = None
        
        try:
            # Save audio bytes to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            print(f"✓ Audio saved to {temp_path} (size: {len(audio_bytes) / 1024:.1f}KB)")
            
            # Transcribe audio using Faster Whisper
            print(f"🔄 Transcribing with {self.model_size}...")
            segments, info = self.model.transcribe(
                temp_path,
                beam_size=5,
                language="en",
                vad_filter=True,
                word_timestamps=False  # Faster transcription
            )
            
            # Process segments
            segments_list = []
            full_text = []
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                segments_list.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                })
                full_text.append(segment.text.strip())
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            # Calculate average confidence (logprob to 0-1 range)
            avg_confidence = (total_confidence / segment_count) if segment_count > 0 else 0.0
            confidence = min(1.0, max(0.0, 1.0 + (avg_confidence / 2.0)))
            
            duration = time.time() - start_time
            print(f"✓ Transcription complete in {duration:.2f}s (confidence: {confidence:.2f})")
            
            return {
                "transcript": " ".join(full_text).strip(),
                "confidence": float(confidence),
                "language": info.language,
                "duration": info.duration if hasattr(info, 'duration') else 0.0,
                "segments": segments_list
            }
            
        except Exception as e:
            print(f"Error in STT processing: {e}")
            traceback.print_exc()
            return {
                "transcript": "",
                "error": str(e),
                "confidence": 0.0,
                "segments": []
            }
            
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"Warning: Failed to delete temp file {temp_path}: {e}")
