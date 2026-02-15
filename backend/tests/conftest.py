"""
Pytest Configuration and Fixtures
"""
import sys
from pathlib import Path
from uuid import uuid4

import pytest

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from domain.enums import ActionPriority, BudgetStatus, ExpenseCategory
from domain.models import ActionItem, Analysis, Expense, Goal, Recommendation


# ==================== FIXTURES ====================

@pytest.fixture
def sample_expense():
    """Sample expense for testing."""
    return Expense(
        description="kahve 50 TL",
        amount=50.0,
        category=ExpenseCategory.FOOD,
    )


@pytest.fixture
def sample_expenses():
    """Multiple sample expenses."""
    return [
        Expense(description="kahve 50 TL", amount=50.0, category=ExpenseCategory.FOOD),
        Expense(description="uber 120 TL", amount=120.0, category=ExpenseCategory.TRANSPORT),
        Expense(description="laptop 8000 TL", amount=8000.0, category=ExpenseCategory.SHOPPING),
        Expense(description="market 300 TL", amount=300.0, category=ExpenseCategory.FOOD),
    ]


@pytest.fixture
def sample_analysis(sample_expenses):
    """Sample analysis for testing."""
    return Analysis(
        total_expenses=8470.0,
        daily_rate=1210.0,
        monthly_projection=36300.0,
        days_analyzed=7,
        category_breakdown={
            "FOOD": 350.0,
            "TRANSPORT": 120.0,
            "SHOPPING": 8000.0,
        },
        budget_status=BudgetStatus.OVER_BUDGET,
        income=15000.0,
        remaining_budget=-21300.0,
        usage_percentage=242.0,
        trends=[
            "Highest spending: SHOPPING (₺8,000)",
            "Monthly projection exceeds income by 142%",
        ],
    )


@pytest.fixture
def sample_recommendation(sample_analysis):
    """Sample recommendation for testing."""
    return Recommendation(
        analysis_id=sample_analysis.id,
        summary="Your spending is 242% of income due to a large electronics purchase.",
        recommendations=[
            "Defer non-essential large purchases",
            "Set up automatic savings",
            "Reduce food delivery",
        ],
        action_items=[
            ActionItem(
                description="Defer non-essential large purchases",
                priority=ActionPriority.HIGH,
                potential_savings=5000.0,
            ),
            ActionItem(
                description="Set up automatic savings",
                priority=ActionPriority.HIGH,
                potential_savings=1500.0,
            ),
            ActionItem(
                description="Reduce food delivery",
                priority=ActionPriority.MEDIUM,
                potential_savings=500.0,
            ),
        ],
        goals=[
            Goal(
                description="Build ₺5,000 emergency fund",
                current_value=0.0,
                target_value=5000.0,
                timeframe="3 months",
            ),
            Goal(
                description="Reduce monthly spending to ₺12,000",
                current_value=36300.0,
                target_value=12000.0,
                timeframe="1 month",
            ),
        ],
    )


# ==================== MOCK LLM ====================

class MockLLMService:
    """Mock LLM service for testing."""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.fast_model = "llama3.2:1b"
        self.accurate_model = "llama3.2:3b"
        self.strategy = "auto"
        self.timeout = 30.0
    
    def select_model(self, task_type: str) -> str:
        """Mock model selection."""
        return self.fast_model if task_type != "recommend" else self.accurate_model
    
    async def generate(
        self,
        prompt: str,
        system: str = "",
        task_type: str = "auto",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Mock LLM generation."""
        # Return predefined responses based on task type
        if task_type == "classify":
            return "FOOD"
        elif task_type == "recommend":
            return """
SUMMARY:
Your spending is well-balanced overall.

ACTIONS:
- [HIGH] Create a monthly budget plan
- [MEDIUM] Track daily expenses

GOALS:
- Build emergency fund
- Reduce discretionary spending
"""
        return "Mock response"
    
    async def check_health(self) -> bool:
        """Mock health check."""
        return True
    
    async def __aenter__(self):
        """Mock context manager."""
        return self
    
    async def __aexit__(self, *args):
        """Mock context manager."""
        pass


@pytest.fixture
def mock_llm():
    """Mock LLM service."""
    return MockLLMService()


# ==================== MOCK TOOLS ====================

class MockSearchTool:
    """Mock search tool for testing."""
    
    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Mock search."""
        return [
            {"title": "Product 1", "url": "http://example.com/1", "snippet": "Price: ₺100"},
            {"title": "Product 2", "url": "http://example.com/2", "snippet": "Price: ₺150"},
        ]
    
    async def search_product_price(self, product_name: str) -> str:
        """Mock product search."""
        return f"Found {product_name} for ₺100-₺150"


@pytest.fixture
def mock_search_tool():
    """Mock search tool."""
    return MockSearchTool()


# ==================== ASYNC HELPERS ====================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
