"""
Strategist Agent - Agent 4
Generates financial recommendations and strategies.
"""
import re

from domain.enums import ActionPriority
from domain.models import ActionItem, Analysis, Goal, Recommendation
from core.prompts import Prompts, format_budget_info, format_categories, format_trends

from .base_agent import BaseAgent


class StrategistAgent(BaseAgent):
    """Financial strategist agent (Agent 4).
    
    Generates personalized financial recommendations and action plans
    based on analysis results.
    
    Features:
    - LLM-generated recommendations
    - Status-based action items with priorities
    - Financial goals with tracking metrics
    - Category-specific advice
    """
    
    def __init__(self, llm_service):
        """Initialize strategist agent.
        
        Args:
            llm_service: LLM service for recommendation generation
        """
        super().__init__("Strategist")
        self.llm = llm_service
    
    @property
    def role(self) -> str:
        return "Generates personalized financial strategies and recommendations"
    
    async def execute(self, analysis: Analysis) -> Recommendation:
        """
        Generate recommendations.
        
        Args:
            analysis: Budget analysis
            
        Returns:
            Recommendation entity
        """
        self.log_start(f"Generating strategy for analysis {analysis.id}")
        
        # Generate LLM recommendations
        llm_text = await self._generate_llm_recommendations(analysis)
        
        # Parse response
        summary, recommendations = self._parse_response(llm_text)
        
        # Generate structured action items
        actions = self._generate_actions(analysis)
        
        # Generate goals
        goals = self._generate_goals(analysis)
        
        recommendation = Recommendation(
            summary=summary,
            recommendations=recommendations,
            action_items=actions,
            goals=goals,
            analysis_id=analysis.id,
        )
        
        self.log_complete(f"Strategy: {len(recommendations)} recs, {len(actions)} actions")
        return recommendation
    
    async def _generate_llm_recommendations(self, analysis: Analysis) -> str:
        """Generate recommendations using LLM.
        
        Args:
            analysis: Budget analysis with metrics
            
        Returns:
            str: LLM-generated recommendation text
        """
        prompt = Prompts.STRATEGIST_PROMPT.format(
            total=analysis.total_expenses,
            daily=analysis.daily_rate,
            monthly=analysis.monthly_projection,
            days=analysis.days_analyzed,
            budget_info=format_budget_info(
                analysis.budget_status.value,
                analysis.income,
                analysis.remaining_budget,
                analysis.usage_percentage,
            ),
            categories=format_categories(analysis.category_breakdown),
            trends=format_trends(analysis.trends),
        )
        
        return await self.llm.generate(
            prompt,
            system=Prompts.STRATEGIST_SYSTEM,
            task_type="recommend",
            temperature=0.8,
        )
    
    def _parse_response(self, text: str) -> tuple[str, list[str]]:
        """Parse LLM response into summary and recommendations.
        
        Args:
            text: LLM response text
            
        Returns:
            tuple: (summary, list of recommendations)
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        summary = ""
        recommendations = []
        
        for line in lines:
            # Skip headers
            if line.startswith('#') or 'status' in line.lower() or 'recommendation' in line.lower():
                continue
            
            # Check if it's a numbered/bulleted item
            if re.match(r'^\d+\.|\-|\*', line):
                cleaned = re.sub(r'^\d+\.\s*|^[-*]\s*', '', line)
                if cleaned:
                    recommendations.append(cleaned)
            elif not summary and len(line) > 20:
                summary = line
        
        # Fallbacks
        if not summary:
            summary = "Budget analysis completed."
        if not recommendations:
            recommendations = ["Track your expenses regularly.", "Create a budget plan."]
        
        return summary, recommendations
    
    def _generate_actions(self, analysis: Analysis) -> list[ActionItem]:
        """Generate action items based on budget status.
        
        Args:
            analysis: Budget analysis with status
            
        Returns:
            list[ActionItem]: Prioritized action items
        """
        actions = []
        status = analysis.budget_status
        
        # Calculate potential monthly reduction
        monthly_reduction = analysis.monthly_projection * 0.1 if analysis.monthly_projection else 0
        
        # Get top 2 categories for targeted recommendations
        top_categories = []
        if analysis.category_breakdown:
            sorted_cats = sorted(
                analysis.category_breakdown.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            top_categories = sorted_cats[:2]
        
        if status.value == "HEALTHY":
            actions.extend([
                ActionItem(
                    "Track your weekly expenses",
                    ActionPriority.LOW,
                    "Budget control",
                    potential_savings=0
                ),
                ActionItem(
                    "Set a savings goal",
                    ActionPriority.LOW,
                    "Long-term planning",
                    potential_savings=monthly_reduction * 2
                ),
            ])
        elif status.value == "WARNING":
            # Specific to top categories
            if top_categories:
                top_cat = top_categories[0]
                actions.append(
                    ActionItem(
                        f"Reduce {top_cat[0]} spending by 15%",
                        ActionPriority.MEDIUM,
                        f"Highest spending category ({top_cat[1]:.0f} TL)",
                        potential_savings=(top_cat[1] * 0.15 * 30 / analysis.days_analyzed)
                    )
                )
            
            actions.append(
                ActionItem(
                    "Cancel unnecessary subscriptions",
                    ActionPriority.MEDIUM,
                    "Reduce recurring costs",
                    potential_savings=monthly_reduction
                )
            )
        else:  # OVER_BUDGET - Very specific actions
            if top_categories:
                # Action for #1 category
                top_cat = top_categories[0]
                actions.append(
                    ActionItem(
                        f"URGENT: Cut {top_cat[0]} spending by 30%",
                        ActionPriority.HIGH,
                        f"Highest category ({top_cat[1]:.0f} TL, {top_cat[1]/analysis.total_expenses*100:.0f}% of budget)",
                        potential_savings=(top_cat[1] * 0.30 * 30 / analysis.days_analyzed)
                    )
                )
                
                # Action for #2 category if exists
                if len(top_categories) > 1:
                    second_cat = top_categories[1]
                    actions.append(
                        ActionItem(
                            f"Reduce {second_cat[0]} spending by 20%",
                            ActionPriority.HIGH,
                            f"Second highest category ({second_cat[1]:.0f} TL)",
                            potential_savings=(second_cat[1] * 0.20 * 30 / analysis.days_analyzed)
                        )
                    )
            
            # General emergency action
            actions.append(
                ActionItem(
                    "Stop all non-essential spending immediately",
                    ActionPriority.URGENT,
                    "Budget at critical level",
                    potential_savings=monthly_reduction * 2
                )
            )
        
        # Add extra action for very high spending category (>40%)
        if analysis.category_breakdown:
            for cat, amount in analysis.category_breakdown.items():
                pct = (amount / analysis.total_expenses * 100) if analysis.total_expenses > 0 else 0
                if pct > 40 and not any(cat in a.description for a in actions):
                    category_savings = (amount * 0.15 * 30 / analysis.days_analyzed)
                    actions.append(
                        ActionItem(
                            f"Create savings plan for {cat} category",
                            ActionPriority.MEDIUM,
                            f"Excessively high percentage ({pct:.1f}%)",
                            potential_savings=category_savings
                        )
                    )
                    break
        
        return actions
    
    def _generate_goals(self, analysis: Analysis) -> list[Goal]:
        """Generate financial goals."""
        goals = []
        
        # Daily goal: -10%
        goals.append(
            Goal(
                "Daily spending target",
                analysis.daily_rate,
                analysis.daily_rate * 0.9,
                "This month",
            )
        )
        
        # Monthly goal: -15%
        goals.append(
            Goal(
                "Monthly spending target",
                analysis.monthly_projection,
                analysis.monthly_projection * 0.85,
                "This month",
            )
        )
        
        return goals
