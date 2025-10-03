# lightweight Python base
FROM python:3.11-slim

WORKDIR /app

# install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy rest of app
COPY . .

# expose app port
EXPOSE 8000

# run your app with uvicorn for FastAPI
CMD ["python", "-m", "uvicorn", "src.apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
