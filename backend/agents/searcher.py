"""
Searcher Agent - Agent 2
Searches for product prices online.
"""
from domain.models import Expense

from .base_agent import BaseAgent


class SearcherAgent(BaseAgent):
    """Product price searcher agent (Agent 2).
    
    Researches market prices for high-value expenses or items
    with unknown prices via web search.
    
    Features:
    - Searches items >= threshold OR amount = 0.0
    - DuckDuckGo web search integration
    - Enriches expenses with market data
    - Marks searched items in metadata
    """
    
    def __init__(self, search_tool, threshold: float = 100.0):
        """Initialize searcher agent.
        
        Args:
            search_tool: Web search tool instance
            threshold: Minimum amount (TL) to trigger search
        """
        super().__init__("Searcher")
        self.search = search_tool
        self.threshold = threshold
    
    @property
    def role(self) -> str:
        return "Researches market prices for high-value products"
    
    async def execute(self, expenses: list[Expense]) -> list[Expense]:
        """
        Search for high-value expenses.
        
        Args:
            expenses: List of expenses
            
        Returns:
            Enriched expenses
        """
        # Search for expenses that either:
        # 1. Have amount >= threshold, OR
        # 2. Have amount = 0 (couldn't parse price, might be valuable item)
        searchable = [
            e for e in expenses 
            if e.amount >= self.threshold or e.amount == 0.0
        ]
        
        if not searchable:
            self.logger.info("No expenses to search")
            return expenses
        
        self.log_start(f"Searching {len(searchable)} items (high-value or unknown price)")
        
        for expense in searchable:
            try:
                results = await self.search.search_product_price(expense.description)
                if results:
                    expense.metadata["search_results"] = results[:3]
                    expense.metadata["searched"] = True
                    self.logger.debug(f"Found {len(results)} results for '{expense.description}'")
            except Exception as e:
                self.log_error(f"search '{expense.description}'", e)
                continue
        
        self.log_complete("Search")
        return expenses
