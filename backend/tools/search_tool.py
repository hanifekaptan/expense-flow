"""
Search Tool
DuckDuckGo web search for product prices.
"""
from typing import Optional

from ddgs import DDGS
from loguru import logger


class SearchTool:
    """Web search tool using DuckDuckGo.
    
    Provides price research capabilities for expenses by searching
    the web for product information and prices.
    
    Features:
    - DuckDuckGo text search (no API key required)
    - Configurable result limit
    - Turkish language support
    - Structured result format (title, link, snippet)
    """
    
    def __init__(self, max_results: int = 5):
        """Initialize search tool.
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
    
    async def search(self, query: str, max_results: Optional[int] = None) -> list[dict]:
        """Execute web search using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Override default max results for this search
            
        Returns:
            list[dict]: Search results with title, link, snippet
            Empty list if search fails
        """
        limit = max_results or self.max_results
        logger.info(f"Searching: '{query}' (limit={limit})")
        
        try:
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=limit)
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    })
            
            logger.info(f"Found {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def search_product_price(self, product: str) -> list[dict]:
        """Search specifically for product prices.
        
        Appends 'fiyat' (price in Turkish) to the query for better results.
        
        Args:
            product: Product name to search for
            
        Returns:
            list[dict]: Search results focused on pricing information
        """
        query = f"{product} fiyat"
        return await self.search(query)
