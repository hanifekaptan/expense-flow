"""
Orchestrator Service
Coordinates all agents for complete workflow.
"""
import time
from typing import Optional

from loguru import logger

from agents.analyst import AnalystAgent
from agents.classifier import ClassifierAgent
from agents.searcher import SearcherAgent
from agents.strategist import StrategistAgent
from core.config import config
from domain.models import Analysis, Expense, Recommendation
from services.llm_service import LLMService
from services.storage import StorageService
from tools.search_tool import SearchTool


class Orchestrator:
    """Multi-agent orchestrator coordinating the complete workflow.
    
    Manages the 4-stage agent pipeline:
    1. Classifier → Parse and categorize expenses
    2. Searcher → Research prices via web search (optional)
    3. Analyst → Calculate financial metrics  
    4. Strategist → Generate recommendations
    
    Also handles data persistence after analysis completion.
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        storage: StorageService,
        search_tool: SearchTool,
        enable_search: bool = True,
        search_threshold: float = 100.0,
    ):
        """Initialize orchestrator with required services.
        
        Args:
            llm_service: LLM service for agent AI capabilities
            storage: Storage service for data persistence
            search_tool: Web search tool for price research
            enable_search: Whether to enable searcher agent
            search_threshold: Minimum amount (TL) to trigger search
        """
        self.llm = llm_service
        self.storage = storage
        
        # Initialize 4 agents
        self.classifier = ClassifierAgent(llm_service)
        self.searcher = SearcherAgent(search_tool, search_threshold) if enable_search else None
        self.analyst = AnalystAgent(enable_code_executor=config.enable_code_executor)
        self.strategist = StrategistAgent(llm_service)
        
        logger.info("Orchestrator initialized with 4 agents")
    
    async def analyze_expenses(
        self,
        expense_texts: list[str],
        income: Optional[float] = None,
        days_analyzed: int = 1,
        enable_search: bool = True,
    ) -> dict:
        """
        Execute complete multi-agent workflow.
        
        Args:
            expense_texts: List of expense descriptions
            income: Optional monthly income
            days_analyzed: Number of days in analysis
            enable_search: Whether to use searcher agent
            
        Returns:
            Complete result with expenses, analysis, recommendation
        """
        start_time = time.time()
        
        logger.info(f"🚀 Starting multi-agent workflow: {len(expense_texts)} expenses")
        
        # ==================== STAGE 1: CLASSIFY ====================
        logger.info("📋 Stage 1: Classifier Agent")
        expenses = await self.classifier.execute(expense_texts)
        
        if not expenses:
            raise ValueError("No expenses were successfully classified")
        
        # ==================== STAGE 2: SEARCH (Optional) ====================
        if enable_search and self.searcher:
            logger.info("🔍 Stage 2: Searcher Agent")
            expenses = await self.searcher.execute(expenses)
        else:
            logger.info("⏭️  Stage 2: Search skipped")
        
        # ==================== STAGE 3: ANALYZE ====================
        logger.info("📊 Stage 3: Analyst Agent")
        analysis = await self.analyst.execute(expenses, days_analyzed, income)
        
        # ==================== STAGE 4: STRATEGIZE ====================
        logger.info("💡 Stage 4: Strategist Agent")
        recommendation = await self.strategist.execute(analysis)
        
        # ==================== STAGE 5: SAVE ====================
        logger.info("💾 Stage 5: Storage")
        await self.storage.save_expenses(expenses)
        await self.storage.save_analysis(analysis)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Workflow complete in {processing_time_ms:.0f}ms")
        
        return {
            "expenses": expenses,
            "analysis": analysis,
            "recommendation": recommendation,
            "processing_time_ms": processing_time_ms,
        }
    
    async def get_analysis_history(self) -> list[Analysis]:
        """Retrieve all past analyses.
        
        Returns:
            list[Analysis]: All saved analyses
        """
        return await self.storage.load_all_analyses()
    
    async def get_expenses(self) -> list[Expense]:
        """Retrieve all saved expenses.
        
        Returns:
            list[Expense]: All saved expenses
        """
        return await self.storage.load_expenses()
