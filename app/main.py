from fastapi import FastAPI

app = FastAPI(
    title="Legal RAG Assistant API",
    description="API for the Legal RAG Assistant, providing retrieval and reasoning services.",
    version="0.1.0",
)

@app.get("/health", tags=["Status"])
async def health_check():
    """Endpoint to check if the API is running."""
    return {"status": "ok"}
