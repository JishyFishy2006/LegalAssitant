# 🐳 Docker Setup for Legal Assistant

This guide explains how to run the Legal Assistant application using Docker and Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 8GB RAM available for Ollama models

### 1. Build and Run
```bash
# From the project root directory
docker compose up --build
```

This will start two services:
- **Ollama**: LLM service running on port 11434
- **Legal Assistant**: Your FastAPI application on port 8000

### 2. Access the Application
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables
The application uses these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `localhost` | Ollama service hostname |
| `OLLAMA_PORT` | `11434` | Ollama service port |
| `OLLAMA_API` | `http://ollama:11434` | Full Ollama API URL |

### Volumes
- `ollama_models`: Persists Ollama model weights
- `./data`: Your legal document indexes
- `./models`: Downloaded Whisper and TTS models

## 📦 First Run

On first run, Docker will:
1. Pull the Python 3.11-slim base image
2. Install system dependencies (ffmpeg)
3. Install Python packages from requirements.txt
4. Pull the Ollama image
5. Download required LLM models (this may take time)

## 🛠️ Development

### Rebuild After Code Changes
```bash
docker compose up --build
```

### View Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs legal-assistant
docker compose logs ollama
```

### Stop Services
```bash
docker compose down
```

### Clean Up (removes volumes)
```bash
docker compose down -v
```

## 🔍 Troubleshooting

### Port Already in Use
If you get "Address already in use" errors:
```bash
# Stop local services first
pkill -f uvicorn
pkill -f "npm run dev"

# Then start Docker
docker compose up --build
```

### Ollama Model Issues
If Ollama can't find models:
```bash
# Check Ollama logs
docker compose logs ollama

# Pull models manually
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text
```

### Memory Issues
If you encounter memory issues:
1. Increase Docker Desktop memory limit (8GB+ recommended)
2. Use smaller models in Ollama
3. Check system memory usage

## 🌐 Network Configuration

- **Ollama**: Accessible at `http://ollama:11434` from within Docker network
- **Legal Assistant**: Accessible at `http://localhost:8000` from host machine
- **Frontend**: Can still run locally on `http://localhost:3000` and proxy to Docker backend

## 📝 Notes

- The application runs in production mode (no `--reload` flag)
- Models are cached in Docker volumes for faster subsequent runs
- Audio processing requires ffmpeg (included in Docker image)
- Data persistence ensures your indexes and models survive container restarts
