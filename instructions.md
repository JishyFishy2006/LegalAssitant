# Tokenized, testable build steps

## 0. Environment
- [T0.1] Install Ollama & model
- [T0.2] Set up Python venv & install deps

## 1. Data ingestion (PDF + HTML/JSON)

**--> NOTE: At this stage, you should add your own data files. Follow the examples in the `data/` subdirectories I've created. Populate `data/sources/manifests/` with your own JSON manifests, and place the corresponding source PDFs, HTML, and JSON files in the appropriate `data/sources/` subdirectories.**
- [T1.1] Add manifests to `data/sources/manifests/`
- [T1.2] Fetch PDFs → `data/sources/pdf/`
- [T1.3] Fetch HTML/JSON → `data/sources/html/` / `json/`
- [T1.4] Parse PDFs → `data/processed/text/`
- [T1.5] Parse HTML → `data/processed/text/`
- [T1.6] Normalize → `data/processed/records.jsonl`

## 2. Index build
- [T2.1] Build FAISS index + meta.sqlite
- [T2.2] Sanity query against index

## 3. Pipeline wiring
- [T3.1] Configure `.env`
- [T3.2] Start API → GET `/health`
- [T3.3] Full flow (text input)
- [T3.4] Full flow (audio input)

## 4. UI check
- [T4.1] Run Vite web app → record, send, render, play

## 5. Quality gates
- [T5.1] Run RAG eval (`scripts/eval_ragas.py`)
- [T5.2] Run all unit tests

---

## Node contracts

**STTNode**
- In: WAV/PCM bytes
- Out: transcript text (+ timings optional)

**RetrieverNode**
- In: query
- Out: candidate chunks

**RerankerNode**
- In: query + candidates
- Out: ranked candidates

**ReasonNode**
- In: query + passages
- Out: JSON string

**StructureNode**
- In: JSON string
- Out: validated JSON object

**TTSNode**
- In: text
- Out: audio bytes + mime type
