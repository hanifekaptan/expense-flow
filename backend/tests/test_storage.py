"""
Storage Service Tests - Essential tests only
"""
import asyncio
import tempfile
from pathlib import Path

import pytest

from domain.models import Expense
from domain.enums import ExpenseCategory
from services.storage import StorageService


@pytest.fixture
def temp_storage(monkeypatch):
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        # Monkeypatch config to use temp directory
        monkeypatch.setattr('services.storage.config.expenses_file', tmpdir_path / 'expenses.json')
        monkeypatch.setattr('services.storage.config.analyses_dir', tmpdir_path / 'analyses')
        
        service = StorageService()
        yield service


def test_expenses_save_and_load(temp_storage):
    """Test saving and loading expenses."""
    expenses = [
        Expense(description="test 1", amount=100.0, category=ExpenseCategory.FOOD),
        Expense(description="test 2", amount=200.0, category=ExpenseCategory.TRANSPORT),
    ]
    
    # Save
    asyncio.run(temp_storage.save_expenses(expenses))
    
    # Load
    loaded = asyncio.run(temp_storage.load_expenses())
    
    assert len(loaded) == 2
    assert loaded[0].description == "test 1"
    assert loaded[1].amount == 200.0


def test_analysis_save_and_load(temp_storage, sample_analysis):
    """Test saving and loading analysis."""
    # Save
    analysis_id = asyncio.run(temp_storage.save_analysis(sample_analysis))
    
    assert analysis_id is not None
    
    # Load
    loaded = asyncio.run(temp_storage.load_analysis(analysis_id))
    
    assert loaded is not None
    assert loaded.total_expenses == sample_analysis.total_expenses
    assert loaded.budget_status == sample_analysis.budget_status


def test_list_analyses(temp_storage, sample_analysis):
    """Test listing all analyses."""
    # Save analysis
    id1 = asyncio.run(temp_storage.save_analysis(sample_analysis))
    
    # List
    analyses = asyncio.run(temp_storage.list_analyses())
    
    assert len(analyses) >= 1
    assert any(a["id"] == id1 for a in analyses)
