# Dependencies for FastAPI application
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

def get_settings():
    """Get application settings from environment variables."""
    return {
        "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
        "k_semantic": int(os.getenv("K_SEMANTIC", 10)),
        "k_keyword": int(os.getenv("K_KEYWORD", 10)),
        "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD", 0.0)),
        "rrf_beta": float(os.getenv("RRF_BETA", 0.7))
    }
