#!/bin/bash

# Docker Setup Script for Legal Assistant
echo "🐳 Setting up Legal Assistant with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop any existing services
echo "🛑 Stopping existing services..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Wait a moment for services to stop
sleep 2

# Check if ports are available
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is still in use. Please stop the service manually."
    exit 1
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    echo "⚠️  Port 3000 is still in use. Please stop the service manually."
    exit 1
fi

# Build and start services
echo "🚀 Building and starting Docker services..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Pull required Ollama models
echo "📥 Pulling required Ollama models..."
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.2:1b

# Wait for models to be ready
echo "⏳ Waiting for models to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend is not responding"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running at http://localhost:11434"
    echo "📋 Available models:"
    curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "   (install jq to see model names)"
else
    echo "❌ Ollama is not responding"
fi

echo ""
echo "🎉 Docker setup complete!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Ollama: http://localhost:11434"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop services: docker compose down"
echo "   Restart: docker compose restart"
echo "   Clean up: docker compose down -v"