"""Unit tests for OllamaClient."""

import pytest
from unittest.mock import Mock, patch
from src.core.llm.ollama_client import OllamaClient


class TestOllamaClient:
    """Test cases for OllamaClient."""
    
    def test_init_default_host_port(self):
        """Test OllamaClient initialization with default host and port."""
        with patch('src.core.llm.ollama_client.ollama.Client') as mock_client:
            client = OllamaClient()
            mock_client.assert_called_once_with(host="http://ollama:11434")
            assert client.client == mock_client.return_value
    
    def test_init_custom_host_port(self):
        """Test OllamaClient initialization with custom host and port."""
        with patch('src.core.llm.ollama_client.ollama.Client') as mock_client:
            client = OllamaClient(ollama_host="localhost", ollama_port="8080")
            mock_client.assert_called_once_with(host="http://localhost:8080")
    
    def test_chat(self):
        """Test chat method."""
        with patch('src.core.llm.ollama_client.ollama.Client') as mock_client:
            client = OllamaClient()
            mock_response = {"message": "Hello"}
            client.client.chat.return_value = mock_response
            
            messages = [{"role": "user", "content": "Hello"}]
            result = client.chat("llama3.2:1b", messages)
            
            client.client.chat.assert_called_once_with(model="llama3.2:1b", messages=messages)
            assert result == mock_response
    
    def test_embed(self):
        """Test embed method."""
        with patch('src.core.llm.ollama_client.ollama.Client') as mock_client:
            client = OllamaClient()
            mock_response = {"embeddings": [[0.1, 0.2, 0.3]]}
            client.client.embed.return_value = mock_response
            
            result = client.embed("test query", "nomic-embed-text")
            
            client.client.embed.assert_called_once_with(model="nomic-embed-text", input="test query")
            assert result == [0.1, 0.2, 0.3]
    
    def test_generate(self):
        """Test generate method."""
        with patch('src.core.llm.ollama_client.ollama.Client') as mock_client:
            client = OllamaClient()
            mock_response = {"response": "Generated text"}
            client.client.generate.return_value = mock_response
            
            result = client.generate("llama3.2:1b", "test prompt")
            
            client.client.generate.assert_called_once_with(model="llama3.2:1b", prompt="test prompt")
            assert result == mock_response
