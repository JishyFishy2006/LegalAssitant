# Legal RAG Assistant

A voice-enabled Legal Retrieval-Augmented Generation (RAG) Assistant that answers legal questions based on uploaded documents.

It integrates:

🎙️ Speech-to-Text (Whisper)

📖 RAG pipeline with a vector DB for retrieval

🧠 Local LLM reasoning (Ollama, containerized)

🔊 Text-to-Speech

Run everything with Docker Compose — no need to install Ollama or Node.js manually.

## 🚀 Quick Start (Docker Recommended)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd LegalAssitant
```

### 2. Build and Run All Services
```bash
docker compose up --build
```

This launches:

- Frontend → http://localhost:3000
- Backend API → http://localhost:8000
- API Docs → http://localhost:8000/docs
- Ollama API → http://localhost:11434

⚠️ **Note**: Ollama is included as a container in Docker Compose. You do not need to install Ollama manually. The container will run it for you.

### 3. Stop the Stack

If running in foreground:
```bash
Ctrl + C
```

Then clean up:
```bash
docker compose down
```

## 🧪 Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Speech-to-Text:**
```bash
curl -X POST -F "audio_file=@test.wav;type=audio/wav" http://localhost:8000/stt/transcribe
```

## 📂 Project Structure
```
src/         # Backend (FastAPI)
frontend/    # Frontend (React + Vite)
data/        # Storage
  ├── sources/   # Raw documents
  ├── index/     # Vector DB
  └── voices/    # TTS output
models/      # Ollama/Whisper models (mounted via Docker)
scripts/     # Utility scripts
```

## ⚙️ Environment Variables

Create a `.env` in the project root:

```bash
# Backend
OLLAMA_BASE_URL=http://ollama:11434
MODEL_NAME=llama2

# Logging
DEBUG=true
```

## 🔮 Next Steps

- 🔁 Auto-restart policies (already set in docker-compose.yml) to keep containers alive.
- 🧹 Context filtering system → only pass relevant legal questions to the RAG pipeline.
- 📊 Add monitoring for model latency, retrieval stats, and transcription quality.
- 🔒 Secure endpoints for production deployment.

## ⚡ Troubleshooting

**Ports in use** → Change ports in docker-compose.yml.

**Build errors** → Run with --no-cache for a clean rebuild:
```bash
docker compose build --no-cache --progress=plain
```

**Ollama startup issues** → Confirm container is running:
```bash
docker ps
curl http://localhost:11434/api/tags
```

## 📜 License (MIT)

MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.