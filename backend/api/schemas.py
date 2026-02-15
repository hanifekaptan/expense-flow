"""
API Schemas
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==================== REQUEST SCHEMAS ====================

class AnalyzeRequest(BaseModel):
    """Request schema for expense analysis.
    
    Attributes:
        expense_texts: List of expense descriptions to analyze
        income: Optional monthly income for budget calculations
        days_analyzed: Number of days in the analysis period (1-365)
        enable_search: Whether to enable web search for price research
    """
    
    expense_texts: list[str] = Field(
        ...,
        min_length=1,
        description="List of expense descriptions",
        examples=[["kahve 50 TL", "market alışverişi 300 TL"]]
    )
    income: Optional[float] = Field(
        None,
        gt=0,
        description="Monthly income in TL",
        examples=[15000.0]
    )
    days_analyzed: int = Field(
        1,
        ge=1,
        le=365,
        description="Number of days analyzed",
        examples=[7]
    )
    enable_search: bool = Field(
        True,
        description="Whether to use web search for high-value items"
    )


# ==================== RESPONSE SCHEMAS ====================

class ExpenseResponse(BaseModel):
    """Response schema for a single expense.
    
    Attributes:
        id: Unique expense identifier
        text: Expense description
        amount: Expense amount in TL
        category: Expense category
        metadata: Additional data (search results, notes, etc.)
    """
    
    id: UUID
    text: str
    amount: float
    category: str
    metadata: dict


class AnalysisResponse(BaseModel):
    """Response schema for financial analysis.
    
    Attributes:
        id: Unique analysis identifier
        total_spent: Total spending amount
        daily_rate: Average spending per day
        monthly_projection: Projected monthly spending
        category_breakdown: Spending by category
        budget_status: Health status (HEALTHY/WARNING/etc.)
        budget_percentage: Spending as % of income
        insights: Notable trends and patterns
        created_at: Analysis creation timestamp
    """
    
    id: UUID
    total_spent: float
    daily_rate: float
    monthly_projection: float
    category_breakdown: dict[str, float]
    budget_status: str
    budget_percentage: float
    insights: list[str]
    created_at: datetime


class ActionItemResponse(BaseModel):
    """Response schema for action item.
    
    Attributes:
        description: What action to take
        priority: Urgency level (LOW/MEDIUM/HIGH/URGENT)
        potential_savings: Estimated savings if action taken
    """
    
    description: str
    priority: str
    potential_savings: Optional[float] = None


class GoalResponse(BaseModel):
    """Response schema for financial goal.
    
    Attributes:
        description: Goal description
        current_value: Current progress
        target_value: Target to reach
        timeframe: Time period for goal
    """
    
    description: str
    current_value: float
    target_value: float
    timeframe: str


class RecommendationResponse(BaseModel):
    """Response schema for recommendations.
    
    Attributes:
        summary: Overall financial summary
        actions: List of action items to take
        goals: List of financial goals
    """
    
    summary: str
    actions: list[ActionItemResponse]
    goals: list[GoalResponse]


class AnalyzeResponse(BaseModel):
    """Complete response schema for analysis endpoint.
    
    Attributes:
        expenses: All classified expenses
        analysis: Financial metrics and status
        recommendation: Personalized advice and goals
        processing_time_ms: Time taken to process request
    """
    
    expenses: list[ExpenseResponse]
    analysis: AnalysisResponse
    recommendation: RecommendationResponse
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    ollama_available: bool
    timestamp: datetime


class AnalysisListResponse(BaseModel):
    """List of past analyses."""
    
    analyses: list[AnalysisResponse]
    total: int
