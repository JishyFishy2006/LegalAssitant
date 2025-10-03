"""Main FastAPI application with modular routes."""

import sys
import os
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add project root to Python path for imports
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.core.nodes.retriever_faiss import Retriever
from src.core.nodes.reranker_bge import RerankerNode
from src.core.nodes.reason_ollama import ReasonNode
from src.core.nodes.structure_validator import StructureNode
from src.core.nodes.stt_faster_whisper import STTNode
from src.core.nodes.tts_piper import TTSNode

# Import routes and dependencies
from .routes import health, query, stt
from .deps import get_app_components, set_app_components

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - load models on startup, cleanup on shutdown."""
    print("🚀 Starting Legal RAG Assistant API...")
    
    try:
        # Initialize all pipeline components
        components = {}
        components["retriever"] = Retriever()
        components["reranker"] = RerankerNode()
        components["reasoner"] = ReasonNode()
        components["validator"] = StructureNode()
        
        # Initialize STT with offline model
        model_path = PROJECT_ROOT / "models" / "whisper"
        model_path.mkdir(parents=True, exist_ok=True)
        print(f"Initializing STT with model from: {model_path}")
        components["stt"] = STTNode(model_size="tiny.en")
        
        components["tts"] = TTSNode()
        
        # Set components in dependency system
        set_app_components(components)
        
        print("✅ All components loaded successfully")
        yield
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        raise
    finally:
        # Cleanup
        components = get_app_components()
        if "retriever" in components:
            components["retriever"].close()
        print("🔄 Components cleaned up")


# Create FastAPI app
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

# Include routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(stt.router)
