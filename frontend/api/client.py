"""
Backend API Client
"""
from typing import Any, Optional

import httpx


class BudgetAnalystClient:
    """Client for ExpenseFlow backend API."""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url
    
    async def health_check(self) -> dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            dict: Health status including ollama availability
            
        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/health",
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()
    
    async def analyze_expenses(
        self,
        expense_texts: list[str],
        income: Optional[float] = None,
        days_analyzed: int = 7,
        enable_search: bool = True,
    ) -> dict[str, Any]:
        """
        Analyze expenses using multi-agent system.
        
        Args:
            expense_texts: List of expense description strings
            income: Monthly income (optional)
            days_analyzed: Number of days covered by expenses
            enable_search: Whether to enable web search for high-value items
            
        Returns:
            dict: Analysis results including expenses, analysis, and recommendations
            
        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/analyze",
                json={
                    "expense_texts": expense_texts,
                    "income": income,
                    "days_analyzed": days_analyzed,
                    "enable_search": enable_search,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_expenses(self) -> list[dict[str, Any]]:
        """
        Get all expenses.
        
        Returns:
            list: List of expense dictionaries
            
        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/expenses",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def add_expense(
        self,
        description: str,
        amount: float,
        category: str,
    ) -> dict[str, Any]:
        """
        Add a single expense.
        
        Args:
            description: Expense description
            amount: Expense amount
            category: Expense category
            
        Returns:
            dict: Created expense
            
        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/expenses",
                json={
                    "description": description,
                    "amount": amount,
                    "category": category,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
