# Legal RAG Assistant Tuning Guide

This document outlines tunable hyperparameters and configuration options for optimizing the Legal RAG Assistant performance across all pipeline components.

## Key Hyperparameters

### `k_semantic`

- **Type**: `int`
- **Default**: `10`
- **Purpose**: Determines the number of initial candidates to retrieve from the FAISS vector (semantic) search.
- **Tuning Advice**: Increasing this value can improve recall by considering more semantically similar documents, but may also introduce less relevant results and increase processing time. A good starting point is 2-3 times the final desired `k` value.

### `k_keyword`

- **Type**: `int`
- **Default**: `10`
- **Purpose**: Determines the number of initial candidates to retrieve from the BM25 (keyword) search.
- **Tuning Advice**: This value should be high enough to capture documents with important keyword matches. If your queries rely on specific terms, consider increasing this value.

### `similarity_threshold`

- **Type**: `float` (0.0 to 1.0)
- **Default**: `0.0`
- **Purpose**: Sets a minimum cosine similarity score for results from the semantic search. Any document below this threshold will be discarded before the fusion step.
- **Tuning Advice**: The default of `0.0` disables this filter. Start by increasing this to `0.7` or `0.75` if you notice many irrelevant semantic results. Setting it too high may prematurely filter out good candidates.

### `RRF_BETA` (Reciprocal Rank Fusion Beta)

- **Type**: `float` (0.0 to 1.0)
- **Default**: `0.7`
- **Purpose**: This parameter controls the balance between semantic and keyword search in the final ranking. It acts as a weighting factor in the Reciprocal Rank Fusion (RRF) score calculation.
- **How it works**:
  - A value of `1.0` means the ranking is based **100% on semantic search** results.
  - A value of `0.0` means the ranking is based **100% on keyword search** results.
  - A value of `0.7` (the default) means the final score is a mix of 70% of the semantic RRF score and 30% of the keyword RRF score.
- **Tuning Advice**: Start with the default of `0.7`. If you find that the results are too broad or conceptually related but missing key terms, decrease the beta to give more weight to keyword search. If the results are too literal and missing the user's intent, increase the beta to favor semantic search.

## Example Usage (CLI)

To override the `.env` settings for a specific run:

```bash
python scripts/retriever.py "what is the statute of limitations for debt collection?" --k 5 --k_semantic 20 --similarity_threshold 0.75
```

## Model Configuration

### Embedding Model
- **Model**: `nomic-embed-text:latest`
- **Dimension**: 768
- **Max Tokens**: 8192
- **Tunable**: Model selection, chunk size for embeddings

### LLM Model  
- **Model**: `llama3.1:8b`
- **Temperature**: 0.1 (factual mode)
- **Top P**: 0.9
- **Repeat Penalty**: 1.1
- **Max Tokens**: 4096
- **Tunable**: Temperature (0.0-0.3 for factual), top_p, repeat_penalty

## Reranking Parameters

### BGE Reranker
- **top_k**: 5 (final results)
- **batch_size**: 32
- **overlap_weight**: 0.3 (text overlap scoring)
- **original_weight**: 0.7 (original retrieval score)
- **Tunable**: top_k (3-10), overlap_weight (0.1-0.5)

## API Configuration

### FastAPI Settings
- **host**: 0.0.0.0
- **port**: 8000
- **reload**: true (development)
- **workers**: 1
- **Tunable**: workers (1-4), timeout settings

### Audio Processing
- **STT Model**: faster-whisper-base
- **TTS Model**: piper-en_US-lessac-medium
- **Audio Format**: WAV, 16kHz
- **Tunable**: Model sizes, sample rates

## Quality Thresholds

### RAGAS Metrics
- **Faithfulness**: ≥ 0.75
- **Context Recall**: ≥ 0.6  
- **Relevance**: ≥ 0.7
- **Tunable**: Thresholds based on use case requirements

### Response Validation
- **Min Citations**: 1
- **Max Response Length**: 2000 tokens
- **Required Disclaimer**: Legal advice warning
- **Tunable**: Citation requirements, response length limits

## Environment Variables

Key tunable parameters exposed via .env:
- `RETRIEVAL_K`: Number of initial candidates
- `RERANK_TOP_K`: Final result count
- `LLM_TEMPERATURE`: Response creativity
- `RRF_K`: Fusion parameter
- `CHUNK_SIZE`: Document chunking
- `OVERLAP_SIZE`: Chunk overlap
