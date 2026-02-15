"""
Domain Model Tests - Essential tests only
"""
from datetime import datetime
from domain.enums import BudgetStatus, ExpenseCategory
from domain.models import Analysis, Expense


def test_expense_basic(sample_expense):
    """Test basic expense creation and serialization."""
    assert sample_expense.description == "kahve 50 TL"
    assert sample_expense.amount == 50.0
    assert sample_expense.category == ExpenseCategory.FOOD
    
    # Test to_dict
    data = sample_expense.to_dict()
    assert data["description"] == "kahve 50 TL"
    assert data["amount"] == 50.0
    assert data["category"] == "FOOD"
    assert "id" in data


def test_expense_from_dict():
    """Test expense deserialization."""
    data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "description": "test 100 TL",
        "amount": 100.0,
        "category": "TRANSPORT",
        "date": datetime.now().isoformat(),
        "metadata": {},
    }
    
    expense = Expense.from_dict(data)
    
    assert expense.description == "test 100 TL"
    assert expense.amount == 100.0
    assert expense.category == ExpenseCategory.TRANSPORT


def test_analysis_basic(sample_analysis):
    """Test basic analysis creation."""
    assert sample_analysis.total_expenses == 8470.0
    assert sample_analysis.daily_rate == 1210.0
    assert sample_analysis.monthly_projection == 36300.0
    assert sample_analysis.budget_status == BudgetStatus.OVER_BUDGET
    assert len(sample_analysis.category_breakdown) > 0


def test_budget_status_calculation():
    """Test budget status from percentage."""
    assert BudgetStatus.from_percentage(50) == BudgetStatus.HEALTHY
    assert BudgetStatus.from_percentage(85) == BudgetStatus.WARNING
    assert BudgetStatus.from_percentage(150) == BudgetStatus.OVER_BUDGET
