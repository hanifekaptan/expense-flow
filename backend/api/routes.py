"""
API Routes
FastAPI endpoints.
"""
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from api.schemas import (
    ActionItemResponse,
    AnalysisListResponse,
    AnalysisResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    ExpenseResponse,
    GoalResponse,
    HealthResponse,
    RecommendationResponse,
)
from services.llm_service import LLMService
from services.orchestrator import Orchestrator
from services.storage import StorageService
from tools.search_tool import SearchTool

# Initialize router
router = APIRouter()

# Initialize services (will be injected via dependency in main.py)
llm_service: LLMService = None
storage: StorageService = None
orchestrator: Orchestrator = None


def init_services():
    """Initialize all services and dependencies.
    
    Creates instances of LLM service, storage, search tool, and orchestrator.
    Called from main.py during application startup.
    """
    global llm_service, storage, orchestrator
    
    llm_service = LLMService()
    storage = StorageService()
    search_tool = SearchTool()
    orchestrator = Orchestrator(
        llm_service=llm_service,
        storage=storage,
        search_tool=search_tool,
    )
    
    logger.info("Services initialized")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.
    
    Verifies that the API server and Ollama LLM service are running.
    Useful for monitoring and deployment health checks.
    
    Returns:
        HealthResponse: Status and availability information
    """
    try:
        async with llm_service:
            ollama_ok = await llm_service.check_health()
        
        return HealthResponse(
            status="healthy" if ollama_ok else "degraded",
            ollama_available=ollama_ok,
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            ollama_available=False,
            timestamp=datetime.now(),
        )


@router.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_expenses(request: AnalyzeRequest):
    """Main analysis endpoint using multi-agent workflow.
    
    Executes the complete 4-stage agent pipeline:
    1. Classifier Agent: Parse and categorize expenses
    2. Searcher Agent: Research prices via web search (optional)
    3. Analyst Agent: Calculate financial metrics
    4. Strategist Agent: Generate recommendations
    
    Args:
        request: Analysis request with expenses, income, settings
        
    Returns:
        AnalyzeResponse: Complete analysis with expenses, metrics, recommendations
        
    Raises:
        HTTPException: 400 for validation errors, 500 for processing errors
    """
    try:
        logger.info(f"Received analysis request: {len(request.expense_texts)} expenses")
        
        # Execute orchestrator
        async with llm_service:
            result = await orchestrator.analyze_expenses(
                expense_texts=request.expense_texts,
                income=request.income,
                days_analyzed=request.days_analyzed,
                enable_search=request.enable_search,
            )
        
        # Convert to response models
        logger.debug(f"Converting {len(result['expenses'])} expenses to response format")
        expenses_data = [
            ExpenseResponse(
                id=e.id,
                text=e.description,
                amount=e.amount,
                category=e.category.value,
                metadata=e.metadata,
            )
            for e in result["expenses"]
        ]
        
        logger.debug("Converting analysis to response format")
        analysis = result["analysis"]
        logger.debug(f"Analysis attributes: {dir(analysis)}")
        analysis_data = AnalysisResponse(
            id=analysis.id,
            total_spent=analysis.total_expenses,
            daily_rate=analysis.daily_rate,
            monthly_projection=analysis.monthly_projection,
            category_breakdown=analysis.category_breakdown,
            budget_status=analysis.budget_status.value,
            budget_percentage=analysis.usage_percentage,
            insights=analysis.trends,
            created_at=analysis.created_at,
        )
        
        logger.debug("Converting recommendation to response format")
        recommendation = result["recommendation"]
        logger.debug(f"Recommendation attributes: {dir(recommendation)}")
        logger.debug(f"Action items count: {len(recommendation.action_items)}")
        recommendation_data = RecommendationResponse(
            summary=recommendation.summary,
            actions=[
                ActionItemResponse(
                    description=a.description,
                    priority=a.priority.value,
                    potential_savings=a.potential_savings,
                )
                for a in recommendation.action_items
            ],
            goals=[
                GoalResponse(
                    description=g.description,
                    current_value=g.current_value,
                    target_value=g.target_value,
                    timeframe=g.timeframe,
                )
                for g in recommendation.goals
            ],
        )
        
        return AnalyzeResponse(
            expenses=expenses_data,
            analysis=analysis_data,
            recommendation=recommendation_data,
            processing_time_ms=result["processing_time_ms"],
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during analysis",
        )


@router.get("/analyses", response_model=AnalysisListResponse)
async def get_analyses():
    """Retrieve all past analyses.
    
    Returns a list of all saved analyses sorted by creation date (newest first).
    Useful for viewing history and trends over time.
    
    Returns:
        AnalysisListResponse: List of analyses with total count
        
    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        analyses = await orchestrator.get_analysis_history()
        
        analyses_data = [
            AnalysisResponse(
                id=a.id,
                total_spent=a.total_expenses,
                daily_rate=a.daily_rate,
                monthly_projection=a.monthly_projection,
                category_breakdown=a.category_breakdown,
                budget_status=a.budget_status.value,
                budget_percentage=a.usage_percentage,
                insights=a.trends,
                created_at=a.created_at,
            )
            for a in analyses
        ]
        
        return AnalysisListResponse(
            analyses=analyses_data,
            total=len(analyses_data),
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analyses",
        )
