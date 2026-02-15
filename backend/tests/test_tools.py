"""
Tool Tests - Essential tests only
"""
import pytest

from tools.search_tool import SearchTool
from tools.code_executor import CodeExecutor


# ==================== SEARCH TOOL TESTS ====================

@pytest.mark.asyncio
async def test_search_tool_basic():
    """Test basic search functionality."""
    tool = SearchTool()
    
    results = await tool.search("laptop price Turkey", max_results=5)
    
    assert isinstance(results, list)
    assert len(results) <= 5
    
    if results:
        assert "title" in results[0]
        assert "link" in results[0]


@pytest.mark.asyncio
async def test_search_tool_product_price():
    """Test product price search."""
    tool = SearchTool()
    
    results = await tool.search_product_price("macbook air m2")
    
    # search_product_price may return list or string depending on implementation
    assert results is not None
    if isinstance(results, list):
        assert len(results) > 0
    elif isinstance(results, str):
        assert len(results) > 0


# ==================== CODE EXECUTOR TESTS ====================

@pytest.mark.asyncio
async def test_code_executor_basic():
    """Test basic code execution."""
    executor = CodeExecutor()
    
    code = """
x = 10
y = 20
result = x + y
"""
    
    output = await executor.execute(code)
    
    assert output["success"] is True
    assert output["output"] == 30


@pytest.mark.asyncio
async def test_code_executor_calculations():
    """Test mathematical calculations."""
    executor = CodeExecutor()
    
    code = """
prices = [100, 200, 300]
total = sum(prices)
average = total / len(prices)
result = average
"""
    
    output = await executor.execute(code)
    
    assert output["success"] is True
    assert output["output"] == 200.0


@pytest.mark.asyncio
async def test_code_executor_timeout():
    """Test timeout protection."""
    executor = CodeExecutor(timeout=1)
    
    code = """
import time
time.sleep(5)
result = "should timeout"
"""
    
    output = await executor.execute(code)
    
    # Should timeout or fail (RestrictedPython blocks time import)
    assert output["success"] is False
