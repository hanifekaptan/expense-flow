"""
Domain Models
Core business entities.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from .enums import ActionPriority, BudgetStatus, ExpenseCategory


# ==================== EXPENSE ====================

@dataclass
class Expense:
    """Expense entity representing a single spending transaction.
    
    Attributes:
        original_text: Original user input text
        description: Cleaned/parsed description
        amount: Expense amount in TL
        category: Classified expense category
        metadata: Optional additional data (search results, notes, etc.)
        id: Unique identifier
        created_at: Timestamp of creation
    """
    
    description: str
    amount: float
    category: ExpenseCategory
    date: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "description": self.description,
            "amount": self.amount,
            "category": self.category.value,
            "date": self.date.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Create expense instance from dictionary.
        
        Args:
            data: Dictionary with expense fields
            
        Returns:
            Expense: New expense instance
        """
        return cls(
            id=UUID(data["id"]),
            description=data["description"],
            amount=data["amount"],
            category=ExpenseCategory(data["category"]),
            date=datetime.fromisoformat(data["date"]),
            metadata=data.get("metadata", {}),
        )


# ==================== ANALYSIS ====================

@dataclass
class Analysis:
    """Budget analysis entity containing financial metrics and insights.
    
    Attributes:
        expenses: List of all expenses analyzed
        total_spending: Sum of all expense amounts
        category_breakdown: Spending grouped by category
        daily_average: Average spending per day
        highest_expense: Largest single expense
        days_analyzed: Number of days in the analysis period
        income: Optional monthly income reference
        budget_status: Overall financial health status
        budget_percentage: Spending as % of income (if provided)
        remaining_budget: Amount left to spend (if income provided)
        trends: List of notable spending patterns
        id: Unique analysis identifier
        created_at: Timestamp of analysis creation
    """
    
    total_expenses: float
    daily_rate: float
    monthly_projection: float
    days_analyzed: int
    category_breakdown: dict[str, float]
    budget_status: BudgetStatus
    income: Optional[float] = None
    remaining_budget: Optional[float] = None
    usage_percentage: Optional[float] = None
    trends: list[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert expense to dictionary for serialization.
        
        Returns:
            dict: Dictionary representation with all fields
        """
        return {
            "id": str(self.id),
            "total_expenses": self.total_expenses,
            "daily_rate": self.daily_rate,
            "monthly_projection": self.monthly_projection,
            "days_analyzed": self.days_analyzed,
            "category_breakdown": self.category_breakdown,
            "budget_status": self.budget_status.value,
            "income": self.income,
            "remaining_budget": self.remaining_budget,
            "usage_percentage": self.usage_percentage,
            "trends": self.trends,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Analysis":
        """Create analysis instance from dictionary.
        
        Args:
            data: Dictionary with analysis fields
            
        Returns:
            Analysis: New analysis instance
        """
        return cls(
            id=UUID(data["id"]),
            total_expenses=data["total_expenses"],
            daily_rate=data["daily_rate"],
            monthly_projection=data["monthly_projection"],
            days_analyzed=data["days_analyzed"],
            category_breakdown=data["category_breakdown"],
            budget_status=BudgetStatus(data["budget_status"]),
            income=data.get("income"),
            remaining_budget=data.get("remaining_budget"),
            usage_percentage=data.get("usage_percentage"),
            trends=data.get("trends", []),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


# ==================== RECOMMENDATION ====================

@dataclass
class ActionItem:
    """Financial action item recommendation.
    
    Attributes:
        description: What action to take
        priority: Urgency level of this action
        impact: Expected result/benefit
        potential_savings: Estimated money saved (if applicable)
    """
    
    description: str
    priority: ActionPriority
    impact: Optional[str] = None
    potential_savings: Optional[float] = None
    
    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "priority": self.priority.value,
            "impact": self.impact,
            "potential_savings": self.potential_savings,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ActionItem":
        return cls(
            description=data["description"],
            priority=ActionPriority(data["priority"]),
            impact=data.get("impact"),
            potential_savings=data.get("potential_savings"),
        )


@dataclass
class Goal:
    """Financial goal with tracking metrics.
    
    Attributes:
        description: Goal description
        current_value: Current progress amount
        target_value: Target amount to reach
        timeframe: Time period for this goal
        category: Optional category this goal relates to
    """
    
    description: str
    current_value: float
    target_value: float
    timeframe: str
    category: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "timeframe": self.timeframe,
            "category": self.category,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        return cls(
            description=data["description"],
            current_value=data["current_value"],
            target_value=data["target_value"],
            timeframe=data["timeframe"],
            category=data.get("category"),
        )


@dataclass
class Recommendation:
    """Financial recommendation entity with actionable advice.
    
    Attributes:
        summary: Overall financial summary
        recommendations: List of text recommendations
        action_items: Prioritized action items to take
        goals: Financial goals to work towards
        analysis_id: Reference to the analysis this is based on
        id: Unique recommendation identifier
        created_at: Timestamp of creation
    """
    
    summary: str
    recommendations: list[str]
    action_items: list[ActionItem]
    goals: list[Goal]
    analysis_id: UUID
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "summary": self.summary,
            "recommendations": self.recommendations,
            "action_items": [a.to_dict() for a in self.action_items],
            "goals": [g.to_dict() for g in self.goals],
            "analysis_id": str(self.analysis_id),
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Recommendation":
        """Create expense instance from dictionary.
        
        Args:
            data: Dictionary with expense fields
            
        Returns:
            Expense: New expense instance
        """
        return cls(
            id=UUID(data["id"]),
            summary=data["summary"],
            recommendations=data["recommendations"],
            action_items=[ActionItem.from_dict(a) for a in data["action_items"]],
            goals=[Goal.from_dict(g) for g in data["goals"]],
            analysis_id=UUID(data["analysis_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
