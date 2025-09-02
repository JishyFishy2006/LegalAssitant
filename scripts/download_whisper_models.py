"""Script to download Whisper models for offline use."""
from faster_whisper import download_model
import os

def main():
    """Download Whisper models."""
    # Create models directory if it doesn't exist
    os.makedirs("./models/whisper", exist_ok=True)
    
    print("Downloading Whisper models...")
    
    # Download tiny English model (~75 MB)
    print("\nDownloading tiny.en model...")
    download_model("tiny.en", "./models/whisper")
    
    # Download base English model (~140 MB)
    print("\nDownloading base.en model...")
    download_model("base.en", "./models/whisper")
    
    print("\nAll models downloaded successfully!")
    print(f"Models saved to: {os.path.abspath('./models/whisper')}")

if __name__ == "__main__":
    main()
