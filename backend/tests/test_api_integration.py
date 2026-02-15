"""
API Integration Tests - Essential tests only
"""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create test client with initialized services."""
    from api.routes import init_services
    
    # Initialize services before creating test client
    init_services()
    
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "ollama_available" in data


def test_analyze_basic(client):
    """Test basic analysis endpoint."""
    request_data = {
        "expense_texts": [
            "kahve 50 TL",
            "uber 120 TL",
            "market 300 TL"
        ],
        "income": 15000.0,
        "days_analyzed": 7,
        "enable_search": False
    }
    
    response = client.post("/api/v1/analyze", json=request_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "expenses" in data
    assert "analysis" in data
    assert "recommendation" in data
    assert len(data["expenses"]) == 3


def test_analyze_with_search(client):
    """Test analysis with search enabled."""
    request_data = {
        "expense_texts": ["laptop 8000 TL"],
        "income": 15000.0,
        "days_analyzed": 7,
        "enable_search": True
    }
    
    response = client.post("/api/v1/analyze", json=request_data, timeout=30)
    
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["expenses"]) == 1
    assert "analysis" in data
