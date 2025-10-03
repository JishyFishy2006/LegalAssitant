import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.core.nodes.retriever_faiss import Retriever
from src.core.nodes.reranker_bge import RerankerNode
from src.core.nodes.reason_ollama import ReasonNode
from src.core.nodes.structure_validator import StructureNode
from src.core.nodes.stt_faster_whisper import STTNode
from src.core.nodes.tts_piper import TTSNode

# Load environment variables
load_dotenv()

# Global components (loaded at startup)
app_components = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - load models on startup, cleanup on shutdown."""
    print("🚀 Starting Legal RAG Assistant API...")
    
    try:
        # Initialize all pipeline components
        app_components["retriever"] = Retriever()
        app_components["reranker"] = RerankerNode()
        app_components["reasoner"] = ReasonNode()
        app_components["validator"] = StructureNode()
        
        # Initialize STT with offline model
        model_path = os.path.join(project_root, "models/whisper")
        os.makedirs(model_path, exist_ok=True)
        print(f"Initializing STT with model from: {model_path}")
        app_components["stt"] = STTNode(model_size="tiny.en")
        
        app_components["tts"] = TTSNode()
        
        print("✅ All components loaded successfully")
        yield
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        raise
    finally:
        # Cleanup
        if "retriever" in app_components:
            app_components["retriever"].close()
        print("🔄 Components cleaned up")

app = FastAPI(
    title="Legal RAG Assistant API",
    description="API for the Legal RAG Assistant, providing retrieval and reasoning services.",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---

class QueryRequest(BaseModel):
    query: str
    k: int = 5
    use_reranker: bool = True

class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    sources_used: int
    processing_time: float

class TranscriptionResponse(BaseModel):
    transcript: str
    confidence: float
    language: str
    duration: float
    segments: List[Dict[str, Any]]
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    version: str

# --- API Endpoints ---

@app.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Endpoint to check if the API is running and components are loaded."""
    component_status = {}
    for name, component in app_components.items():
        component_status[name] = "loaded" if component else "failed"
    
    return HealthResponse(
        status="ok" if all(app_components.values()) else "degraded",
        components=component_status,
        version="0.1.0"
    )

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_text(request: QueryRequest):
    """
    Process a text query through the full RAG pipeline.
    T3.3: Full flow (text input) → POST /query with text → JSON response.
    """
    import time
    start_time = time.time()
    
    try:
        # Step 1: Retrieve relevant documents
        retriever = app_components["retriever"]
        retrieved_docs = retriever.search(request.query, k=request.k * 2)  # Get more candidates
        
        if not retrieved_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Step 2: Rerank documents (optional)
        final_docs = retrieved_docs
        if request.use_reranker:
            reranker = app_components["reranker"]
            final_docs = reranker.process(request.query, retrieved_docs, top_k=request.k)
        else:
            final_docs = retrieved_docs[:request.k]
        
        # Step 3: Generate reasoning response
        reasoner = app_components["reasoner"]
        response = reasoner.process(request.query, final_docs)
        
        # Step 4: Validate and structure response
        validator = app_components["validator"]
        validation_result = validator.process(
            response.get("answer", ""), 
            expected_schema=None
        )
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            answer=response.get("answer", ""),
            citations=response.get("citations", []),
            sources_used=len(final_docs),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

def convert_audio(input_bytes: bytes, input_format: str) -> bytes:
    """Convert audio to 16kHz mono WAV format using ffmpeg."""
    try:
        import subprocess
        import tempfile
        import os
        
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

@app.post("/stt/transcribe", response_model=TranscriptionResponse, tags=["Speech-to-Text"])
async def transcribe_audio(audio_file: UploadFile = File(...)):
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

@app.post("/query/audio", tags=["Query"])
async def query_audio(audio_file: UploadFile = File(...)):
    """
    Process an audio query through the full pipeline.
    T3.4: Full flow (audio input) → POST /query/audio with WAV → transcript → retrieval → reasoning → TTS.
    
    Note: Consider using /stt/transcribe for just getting the transcript.
    """
    import time
    start_time = time.time()
    
    try:
        # Use the new transcribe endpoint for consistency
        stt_response = await transcribe_audio(audio_file)
        
        if not stt_response.transcript:
            raise HTTPException(
                status_code=400, 
                detail=f"Could not transcribe audio: {stt_response.error or 'Unknown error'}"
            )
        
        # Process text query (reuse text pipeline)
        query_request = QueryRequest(
            query=stt_response.transcript, 
            k=5, 
            use_reranker=True
        )
        text_response = await query_text(query_request)
        
        # Text-to-Speech for response
        tts = app_components["tts"]
        tts_result = tts.process(text_response.answer)
        
        processing_time = time.time() - start_time
        
        # Return audio response
        return Response(
            content=tts_result.get("audio_bytes", b""),
            media_type=tts_result.get("mime_type", "audio/wav"),
            headers={
                "X-Transcript": stt_response.transcript,
                "X-Processing-Time": str(processing_time),
                "X-Sources-Used": str(text_response.sources_used)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
