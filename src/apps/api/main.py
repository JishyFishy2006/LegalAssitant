import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
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
        app_components["stt"] = STTNode()
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
            answer=validation_result.get("data", {}).get("answer", response.get("answer", "")),
            citations=response.get("citations", []),
            sources_used=len(final_docs),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/query/audio", tags=["Query"])
async def query_audio(audio_file: UploadFile = File(...)):
    """
    Process an audio query through the full pipeline.
    T3.4: Full flow (audio input) → POST /query/audio with WAV → transcript → retrieval → reasoning → TTS.
    """
    import time
    start_time = time.time()
    
    try:
        # Step 1: Speech-to-Text
        audio_bytes = await audio_file.read()
        stt = app_components["stt"]
        stt_result = stt.process(audio_bytes, mime_type=audio_file.content_type or "audio/wav")
        
        if not stt_result.get("transcript"):
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        transcript = stt_result["transcript"]
        
        # Step 2: Process text query (reuse text pipeline)
        query_request = QueryRequest(query=transcript, k=5, use_reranker=True)
        text_response = await query_text(query_request)
        
        # Step 3: Text-to-Speech
        tts = app_components["tts"]
        tts_result = tts.process(text_response.answer)
        
        processing_time = time.time() - start_time
        
        # Return audio response
        return Response(
            content=tts_result.get("audio_bytes", b""),
            media_type=tts_result.get("mime_type", "audio/wav"),
            headers={
                "X-Transcript": transcript,
                "X-Processing-Time": str(processing_time),
                "X-Sources-Used": str(text_response.sources_used)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
