# Legal Voice RAG MVP — Architecture

## Repository layout
.
├── src/
│ ├── apps/
│ │ ├── api/
│ │ │ ├── main.py
│ │ │ ├── deps.py
│ │ │ └── routes/
│ │ │ ├── stt.py
│ │ │ ├── proscons.py
│ │ │ └── tts.py
│ │ └── web/
│ │ ├── index.html
│ │ ├── vite.config.ts
│ │ └── src/
│ │ ├── App.tsx
│ │ ├── components/
│ │ │ ├── MicRecorder.tsx
│ │ │ ├── ProsConsTable.tsx
│ │ │ └── AudioPlayer.tsx
│ │ └── services/api.ts
│ ├── core/
│ │ ├── graph/
│ │ │ └── pipeline.py
│ │ ├── nodes/
│ │ │ ├── stt_faster_whisper.py
│ │ │ ├── retriever_faiss.py
│ │ │ ├── reranker_bge.py
│ │ │ ├── reason_ollama.py
│ │ │ ├── structure_validator.py
│ │ │ └── tts_piper.py
│ │ ├── llm/
│ │ │ └── ollama_client.py
│ │ ├── rag/
│ │ │ ├── ingest/
│ │ │ │ ├── fetch_pdf.py
│ │ │ │ ├── fetch_htmljson.py
│ │ │ │ ├── parse_pdf.py
│ │ │ │ ├── parse_html.py
│ │ │ │ └── normalize_records.py
│ │ │ ├── build_index.py
│ │ │ ├── chunk.py
│ │ │ ├── embed.py
│ │ │ ├── store.py
│ │ │ └── schemas.py
│ │ ├── prompts/
│ │ │ ├── system_legal.md
│ │ │ └── user_proscons_template.md
│ │ └── schema/
│ │ └── pros_cons.schema.json
│ └── utils/
│ ├── logging.py
│ └── io.py
├── data/
│ ├── sources/
│ │ ├── pdf/
│ │ ├── html/
│ │ ├── json/
│ │ └── manifests/
│ ├── processed/
│ │ ├── text/
│ │ └── records.jsonl
│ ├── index/
│ │ ├── faiss.index
│ │ └── meta.sqlite
│ └── voices/
├── tests/
│ ├── unit/
│ └── e2e/
├── scripts/
│ ├── ingest_sources.py
│ ├── eval_ragas.py
│ └── smoke_cli.py
├── pyproject.toml
├── .env.example
└── README.md