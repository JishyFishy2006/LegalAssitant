"""Ollama client for LLM interactions."""
import ollama
from typing import Dict, Any, List

class OllamaClient:
    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model
    
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
        
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options=options
        )
        return response
    
    def embed(self, text: str, model: str = "nomic-embed-text") -> List[float]:
        """Generate embeddings for text."""
        response = ollama.embed(model=model, input=text)
        return response.embeddings[0]
