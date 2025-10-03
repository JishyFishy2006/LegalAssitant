"""Ollama client for LLM interactions."""
import os
import ollama
from typing import Dict, Any, List

class OllamaClient:
    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model
        
        # Configure Ollama client to use environment variables
        ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        ollama_port = os.getenv("OLLAMA_PORT", "11434")
        
        # Use the new Client API instead of set_host()
        self.client = ollama.Client(host=f"http://{ollama_host}:{ollama_port}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send a chat completion request to Ollama."""
        # Set factual mode defaults
        options = {
            'temperature': 0.1,  # Low creativity for factual accuracy
            'top_p': 0.9,
            'repeat_penalty': 1.1
        }
        
        # Update with any provided options
        if 'options' in kwargs:
            options.update(kwargs.pop('options'))
        
        # Update with remaining kwargs (for backward compatibility)
        options.update({k: v for k, v in kwargs.items() if k in ['temperature', 'top_p', 'repeat_penalty']})
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options=options
        )
        return response
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a completion from Ollama."""
        # Set factual mode defaults
        options = {
            'temperature': 0.1,  # Low creativity for factual accuracy
            'top_p': 0.9,
            'repeat_penalty': 1.1
        }
        
        # Update with any provided options
        if 'options' in kwargs:
            options.update(kwargs.pop('options'))
        
        # Update with remaining kwargs (for backward compatibility)
        options.update({k: v for k, v in kwargs.items() if k in ['temperature', 'top_p', 'repeat_penalty']})
        
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            options=options
        )
        return response
    
    def embed(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """Generate embeddings for text."""
        response = self.client.embed(model=model, input=text)
        return response.embeddings[0]
