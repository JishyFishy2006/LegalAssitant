# Legal RAG Assistant

This project is a voice-enabled Legal RAG (Retrieval-Augmented Generation) Assistant designed to answer legal questions based on a provided set of documents. It uses a FastAPI backend, a vector database for efficient document retrieval, and local AI models for speech-to-text, reasoning, and text-to-speech.

## System Requirements

Before you begin, ensure you have the following installed:

- **Python**: Version 3.9 or higher.
- **ffmpeg**: Required for audio processing. You can install it using Homebrew on macOS (`brew install ffmpeg`) or a package manager on Linux.
- **Ollama**: For running the local language model. Follow the installation instructions at [https://ollama.ai/](https://ollama.ai/).

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd LegalAssitant
    ```

2.  **Create a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Download AI Models:**

    -   **Whisper Models (for Speech-to-Text):**

        ```bash
        python3 scripts/download_whisper_models.py
        ```

    -   **Ollama Language Model (for reasoning):**

        ```bash
        ollama pull llama2
        ```

## Running the Application

To start the FastAPI backend server, run the following command from the project root:

```bash
uvicorn src.apps.api.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Testing the API

You can interact with the API using `curl` or any API client.

-   **Health Check:**

    ```bash
    curl http://127.0.0.1:8000/health
    ```

-   **Voice Transcription:**

    Use one of the test audio files (`test.wav` or `test.aiff`) to test the transcription endpoint:

    ```bash
    curl -X POST -F "audio_file=@test.wav;type=audio/wav" http://127.0.0.1:8000/stt/transcribe
    ```

## Launch Instructions

Follow these steps to launch the Legal Assistant application:

### Prerequisites
- Python 3.9 or higher
- Node.js 16+ and npm
- Ollama installed and running (for local LLM)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd LegalAssitant
```

### 2. Set Up Backend
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to project root
cd ..
```

### 4. Launch the Application

#### Start the Backend Server
In one terminal window, run:
```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Start FastAPI server
uvicorn src.apps.api.main:app --reload --port 8000
```

#### Start the Frontend Development Server
In a second terminal window, run:
```bash
# Navigate to frontend directory
cd frontend

# Start Vite development server
npm run dev
```

### 5. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 6. Verify Installation
- Visit http://localhost:3000 in your web browser
- The application should load without errors
- Try entering a legal query to test the RAG pipeline

## Troubleshooting

### Common Issues
1. **Port Conflicts**: 
   - If port 3000 or 8000 is in use, update the ports in:
     - Frontend: `frontend/vite.config.ts`
     - Backend: Change the port in the `uvicorn` command

2. **Missing Dependencies**:
   - Ensure all Python packages are installed in the virtual environment
   - Run `npm install` in the frontend directory

3. **Ollama Not Running**:
   - Make sure Ollama is installed and running
   - The backend requires Ollama for LLM processing

## Development

### Project Structure
- `src/`: Backend source code
- `frontend/`: React frontend application
- `data/`: Data storage and processing
  - `sources/`: Source documents
  - `index/`: Vector store and metadata
  - `voices/`: Text-to-speech voice files

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
# Backend Configuration
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama2  # or your preferred model

# Optional: Set to enable additional logging
DEBUG=true
```

## License
[Your License Here]