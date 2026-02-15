"""
Agent Tests - Essential tests only
"""
import pytest

from agents.analyst import AnalystAgent
from agents.classifier import ClassifierAgent
from agents.searcher import SearcherAgent
from agents.strategist import StrategistAgent
from domain.enums import BudgetStatus, ExpenseCategory


# ==================== CLASSIFIER TESTS ====================

@pytest.mark.asyncio
async def test_classifier_basic(mock_llm):
    """Test basic expense classification."""
    agent = ClassifierAgent(mock_llm)
    
    expenses = await agent.execute(["kahve 50 TL", "uber 120 TL", "market 300 TL"])
    
    assert len(expenses) == 3
    assert sum(e.amount for e in expenses) == 470.0
    assert all(e.category in ExpenseCategory for e in expenses)


# ==================== SEARCHER TESTS ====================

@pytest.mark.asyncio
async def test_searcher_basic(mock_search_tool, sample_expenses):
    """Test basic search functionality."""
    agent = SearcherAgent(mock_search_tool, threshold=100.0)
    
    enriched = await agent.execute(sample_expenses)
    
    assert len(enriched) == len(sample_expenses)
    # High-value items should be searched
    searched = [e for e in enriched if e.metadata.get("searched")]
    assert len(searched) >= 1


# ==================== ANALYST TESTS ====================

@pytest.mark.asyncio
async def test_analyst_basic(sample_expenses):
    """Test basic financial analysis."""
    agent = AnalystAgent()
    
    analysis = await agent.execute(
        expenses=sample_expenses,
        days_analyzed=7,
        income=15000.0
    )
    
    assert analysis.total_expenses == 8470.0
    assert analysis.daily_rate > 0
    assert analysis.monthly_projection > 0
    assert analysis.budget_status == BudgetStatus.OVER_BUDGET
    assert len(analysis.category_breakdown) > 0


# ==================== STRATEGIST TESTS ====================

@pytest.mark.asyncio
async def test_strategist_basic(mock_llm, sample_analysis):
    """Test basic recommendation generation."""
    agent = StrategistAgent(mock_llm)
    
    recommendation = await agent.execute(sample_analysis)
    
    assert recommendation.summary is not None
    assert len(recommendation.action_items) > 0
    assert len(recommendation.goals) > 0


# ==================== INTEGRATION TEST ====================

@pytest.mark.asyncio
async def test_full_workflow(mock_llm, mock_search_tool):
    """Test complete 4-agent workflow."""
    # Initialize agents
    classifier = ClassifierAgent(mock_llm)
    searcher = SearcherAgent(mock_search_tool, threshold=100.0)
    analyst = AnalystAgent()
    strategist = StrategistAgent(mock_llm)
    
    # Execute workflow
    texts = ["kahve 50 TL", "uber 120 TL", "laptop 8000 TL"]
    
    # Stage 1: Classify
    expenses = await classifier.execute(texts)
    assert len(expenses) == 3
    
    # Stage 2: Search
    expenses = await searcher.execute(expenses)
    
    # Stage 3: Analyze
    analysis = await analyst.execute(
        expenses=expenses,
        days_analyzed=7,
        income=15000.0
    )
    assert analysis.total_expenses > 0
    
    # Stage 4: Recommend
    recommendation = await strategist.execute(analysis)
    assert len(recommendation.action_items) > 0
