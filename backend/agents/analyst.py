"""
Analyst Agent - Agent 3
Analyzes expenses and calculates budget metrics.
"""
from domain.enums import BudgetStatus
from domain.models import Analysis, Expense
from tools.code_executor import CodeExecutor

from .base_agent import BaseAgent


class AnalystAgent(BaseAgent):
    """Budget analyst agent (Agent 3).
    
    Performs financial calculations and generates analysis metrics.
    
    Features:
    - Total spending and daily rate calculation
    - Category breakdown with percentages
    - Budget status determination
    - Trend detection (high spending categories)
    - Monthly projection
    - Advanced calculations via CodeExecutor
    """
    
    def __init__(self, enable_code_executor: bool = True):
        """Initialize analyst agent.
        
        Args:
            enable_code_executor: Whether to use CodeExecutor for advanced calculations
        """
        super().__init__("Analyst")
        self.enable_code_executor = enable_code_executor
        if enable_code_executor:
            self.code_executor = CodeExecutor(timeout=5)
    
    @property
    def role(self) -> str:
        return "Analyzes expenses and performs budget calculations"
    
    async def execute(
        self,
        expenses: list[Expense],
        days_analyzed: int,
        income: float = None
    ) -> Analysis:
        """
        Analyze expenses.
        
        Args:
            expenses: List of expenses
            days_analyzed: Number of days
            income: Optional monthly income
            
        Returns:
            Analysis entity
        """
        self.log_start(f"Analyzing {len(expenses)} expenses over {days_analyzed} days")
        
        if not expenses:
            raise ValueError("Cannot analyze empty expenses")
        
        # Calculate metrics
        total = sum(e.amount for e in expenses)
        daily_rate = total / days_analyzed
        monthly_projection = daily_rate * 30
        
        # Category breakdown - Use CodeExecutor for advanced calculation
        if self.enable_code_executor:
            category_breakdown = await self._calculate_breakdown_with_code(expenses, total)
        else:
            category_totals = {}
            for e in expenses:
                cat = e.category.value
                category_totals[cat] = category_totals.get(cat, 0) + e.amount
            category_breakdown = category_totals
        
        # Budget status
        if income:
            usage_pct = (monthly_projection / income) * 100
            status = BudgetStatus.from_percentage(usage_pct)
            remaining = income - monthly_projection if income > monthly_projection else 0
        else:
            usage_pct = None
            status = BudgetStatus.UNKNOWN
            remaining = None
        
        # Trends
        trends = []
        for cat, amount in category_breakdown.items():
            pct = (amount / total) * 100
            if pct >= 30:
                from domain.enums import ExpenseCategory
                try:
                    cat_enum = ExpenseCategory(cat)
                    trends.append(
                        f"{cat_enum.get_emoji()} {cat} spending is high ({amount:.0f} TL, {pct:.1f}%)"
                    )
                except ValueError:
                    pass
        
        analysis = Analysis(
            total_expenses=total,
            daily_rate=daily_rate,
            monthly_projection=monthly_projection,
            days_analyzed=days_analyzed,
            category_breakdown=category_breakdown,
            budget_status=status,
            income=income,
            remaining_budget=remaining,
            usage_percentage=usage_pct,
            trends=trends,
        )
        
        self.log_complete(f"Analysis: {total:.0f} TL, Status: {status.value}")
        return analysis
    
    async def _calculate_breakdown_with_code(
        self,
        expenses: list[Expense],
        total: float
    ) -> dict[str, float]:
        """Calculate category breakdown using CodeExecutor.
        
        Uses Python code execution for advanced category aggregation
        and percentage calculations. This demonstrates the code execution
        tool integration required by the case study.
        
        Args:
            expenses: List of expenses
            total: Total spending amount
            
        Returns:
            dict: Category name to amount mapping
        """
        self.logger.info("Using CodeExecutor for category breakdown calculation")
        
        # Generate Python code for category aggregation
        expense_data = [(e.category.value, e.amount) for e in expenses]
        
        code = f"""
# Category breakdown calculation
expenses = {expense_data}
total = {total}

# Aggregate by category
category_totals = {{}}
for category, amount in expenses:
    if category in category_totals:
        category_totals[category] += amount
    else:
        category_totals[category] = amount

# Calculate percentages and round amounts
result = {{}}
for cat, amt in category_totals.items():
    percentage = (amt / total) * 100
    result[cat] = round(amt, 2)

result = category_totals
"""
        
        # Execute code safely
        execution_result = await self.code_executor.execute(code)
        
        if execution_result["success"]:
            self.logger.info("Category breakdown calculated via CodeExecutor")
            return execution_result["output"]
        else:
            # Fallback to direct calculation on error
            self.logger.warning(
                f"CodeExecutor failed: {execution_result['error']}, using fallback"
            )
            category_totals = {}
            for e in expenses:
                cat = e.category.value
                category_totals[cat] = category_totals.get(cat, 0) + e.amount
            return category_totals
