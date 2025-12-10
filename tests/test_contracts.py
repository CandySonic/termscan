"""
Tests for contract analysis API
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_api_key

client = TestClient(app)

# Create test API key
test_key_data = create_api_key("Test Client", "enterprise")
TEST_API_KEY = test_key_data["api_key"]
AUTH_HEADER = {"Authorization": f"Bearer {TEST_API_KEY}"}


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert "ai_provider" in response.json()


class TestAuthentication:
    """Test API key authentication"""
    
    def test_missing_api_key(self):
        response = client.post("/v1/contracts/analyze", json={
            "text": "This is a test contract with enough text to pass validation.",
        })
        assert response.status_code == 401
    
    def test_invalid_api_key(self):
        response = client.post(
            "/v1/contracts/analyze",
            json={"text": "This is a test contract with enough text to pass validation."},
            headers={"Authorization": "Bearer invalid_key"},
        )
        assert response.status_code == 401
    
    def test_valid_api_key(self):
        # This will fail without AI configured, but auth should pass
        response = client.post(
            "/v1/contracts/analyze",
            json={"text": "x" * 100},  # Minimum length
            headers=AUTH_HEADER,
        )
        # Either 200 (success) or 500 (AI not configured) - not 401
        assert response.status_code != 401


class TestContractValidation:
    """Test request validation"""
    
    def test_text_too_short(self):
        response = client.post(
            "/v1/contracts/analyze",
            json={"text": "Too short"},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_contract_type(self):
        response = client.post(
            "/v1/contracts/analyze",
            json={
                "text": "x" * 100,
                "type": "invalid_type",
            },
            headers=AUTH_HEADER,
        )
        assert response.status_code == 422


# Run with: pytest tests/ -v
