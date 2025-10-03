# BUILD_STEPS.md

Tokenized, testable build steps for Legal Voice Assistant MVP.  
Goal: ingest legal docs (FCRA/FDCPA, etc.), build RAG index, expose API, wire UI, and test full voice query → response → audio flow.

---

## 0. Environment

- [T0.1] **Install Ollama & models**  
  - Action: `ollama pull nomic-embed-text && ollama pull llama3.1:8b`  
  - Check: `ollama list` shows both models.  
  - ✅ Done when: exit code 0.

- [T0.2] **Python venv & deps**  
  - Action: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`  
  - Check: `python -c "import faiss, fastapi, pydantic, librosa"` runs.  
  - ✅ Done when: exit code 0.

---

## 1. Data Ingestion (PDF + HTML/JSON)

> At this stage, **add your own data files**.  
> Place manifests in `data/sources/manifests/`, and raw files in `data/sources/pdf/`, `data/sources/html/`, or `data/sources/json/`.

- [T1.1] **Add manifests** → `data/sources/manifests/*.json`
- [T1.2] **Fetch PDFs** → `data/sources/pdf/`
- [T1.3] **Fetch HTML/JSON** → `data/sources/html/` & `data/sources/json/`
- [T1.4] **Parse PDFs** → `data/processed/text/`
- [T1.5] **Parse HTML/JSON** → `data/processed/text/`
- [T1.6] **Normalize** → `data/processed/records.jsonl`

### Manifest Schema (example)

```json
{
  "$schema": "https://example.local/legal-source.schema.json",
  "id": "cfpb-fcra-faq-2025-06-01",
  "title": "CFPB: Credit Reporting FAQs",
  "source_url": "https://www.consumerfinance.gov/ask-cfpb/category-credit-reporting/",
  "file_type": "html",
  "jurisdiction": "US-federal",
  "legal_domain": ["FCRA", "credit-reporting"],
  "published_date": "2025-06-01",
  "effective_date": "2025-06-01",
  "version": "2025-06-01",
  "provenance": "CFPB",
  "retrieval_policy": {"allow_cache_days": 90},
  "local_path": "data/sources/html/cfpb-credit-faq.html",
  "checksum": "sha256:...",
  "tags": ["anchor", "official"],
  "licensing": "public",
  "priority": 1
}
Record Schema (normalized JSONL)
json
Copy
Edit
{
  "id": "cfpb-fcra-faq-2025-06-01#p0001#c0001",
  "doc_id": "cfpb-fcra-faq-2025-06-01",
  "jurisdiction": "US-federal",
  "legal_domain": ["FCRA"],
  "effective_date": "2025-06-01",
  "title": "CFPB: Credit Reporting FAQs",
  "section": "Disputing errors",
  "text": "You can dispute an error on your credit report by..."
}
2. Index Build
[T2.1] Build FAISS index + meta.sqlite

Input: data/processed/records.jsonl

Embeddings: nomic-embed-text

Output: index/faiss.index, index/meta.sqlite

[T2.2] Sanity query

Run: scripts/query.py "How long do late payments stay on my credit report?"

✅ Done when: returns ≥1 passage with metadata.

3. Pipeline Wiring
[T3.1] ✅ Configure .env (API keys, DB paths, model names)

[T3.2] ✅ Start API → uvicorn src.apps.api.main:app --reload

GET /health → {status:"ok", components: {...}, version: "0.1.0"}

[T3.3] ✅ Full flow (text input)

POST /query with text → JSON response with answer, citations, processing_time.

[T3.4] ✅ Full flow (audio input)

POST /query/audio with WAV → transcript → retrieval → reasoning → TTS.

✅ Done when: API endpoints functional with fallback responses.

4. UI Check
[T4.1] Run Vite web app

Start: npm run dev

Flow: record mic → send → render transcript → play audio.

✅ Done when: user can “talk to it” in browser.

5. Quality Gates
[T5.1] RAG eval → python scripts/eval_ragas.py

✅ Pass if ≥0.75 faithfulness score.

[T5.2] Run all unit tests → pytest -q

✅ Done when: all green.

Node Contracts
STTNode

In: WAV/PCM bytes

Out: transcript text (+ timings optional)

RetrieverNode

In: query

Out: candidate chunks

RerankerNode

In: query + candidates

Out: ranked candidates

ReasonNode

In: query + passages

Out: JSON string (answer + citations)

StructureNode

In: JSON string

Out: validated JSON object

TTSNode

In: text

Out: audio bytes + mime type

Legal Guardrails
Always prefix answers with: “I am not a lawyer. This is not legal advice.”

Return citations with every answer (doc ID + source URL).

Strip/replace PII (names, SSNs, phone numbers) during ingestion.

Only index authoritative sources (CFPB, FTC, statutes, regs).
