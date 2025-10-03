"""Query processing endpoints."""

import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..deps import get_app_components

router = APIRouter(prefix="/query", tags=["Query"])


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


@router.post("", response_model=QueryResponse)
async def query_text(request: QueryRequest, app_components: Dict = Depends(get_app_components)):
    """
    Process a text query through the full RAG pipeline.
    T3.3: Full flow (text input) → POST /query with text → JSON response.
    """
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


@router.post("/audio")
async def query_audio(audio_file, app_components: Dict = Depends(get_app_components)):
    """
    Process an audio query through the full pipeline.
    T3.4: Full flow (audio input) → POST /query/audio with WAV → transcript → retrieval → reasoning → TTS.
    
    Note: Consider using /stt/transcribe for just getting the transcript.
    """
    from fastapi import UploadFile, File
    from fastapi.responses import Response
    
    start_time = time.time()
    
    try:
        # Use the STT transcribe endpoint for consistency
        from .stt import transcribe_audio
        stt_response = await transcribe_audio(audio_file, app_components)
        
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
        text_response = await query_text(query_request, app_components)
        
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
