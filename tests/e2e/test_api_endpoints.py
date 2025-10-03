"""End-to-end tests for API endpoints."""

import pytest
import requests
from fastapi.testclient import TestClient
from src.apps.api.main import app


class TestAPIEndpoints:
    """End-to-end tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client for API."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_query_endpoint_structure(self, client):
        """Test query endpoint structure (without actual processing)."""
        # This test would require mocking the entire pipeline
        # For now, we'll test the endpoint exists and returns proper error for missing data
        response = client.post("/query", json={"query": "test query"})
        # Should return 500 or 422 depending on implementation
        assert response.status_code in [422, 500]
    
    def test_stt_transcribe_endpoint_structure(self, client):
        """Test STT transcribe endpoint structure."""
        # Test with invalid file
        response = client.post("/stt/transcribe")
        assert response.status_code in [422, 400]  # Missing file
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/health")
        assert "access-control-allow-origin" in response.headers
