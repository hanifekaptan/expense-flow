"""
LLM Service Tests - Essential tests only
"""
import pytest
from services.llm_service import LLMService


def test_llm_initialization():
    """Test LLM service initialization."""
    service = LLMService()
    
    assert service.base_url is not None
    assert service.fast_model is not None
    assert service.accurate_model is not None
    assert service.strategy in ["auto", "fast", "accurate"]


def test_model_selection(monkeypatch):
    """Test intelligent model selection."""
    monkeypatch.setattr('services.llm_service.config.model_strategy', 'auto')
    service = LLMService()
    
    # Fast model for simple tasks
    model = service.select_model("classify")
    assert model == service.fast_model
    
    # Accurate model for complex tasks
    model = service.select_model("recommend")
    assert model == service.accurate_model
