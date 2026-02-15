"""
LLM Prompt Templates
Centralized prompts for all agents.
"""


class Prompts:
    """LLM prompt templates for all agents.
    
    Centralized storage for system prompts and user prompt templates
    used by Classifier and Strategist agents.
    
    Includes:
    - CLASSIFIER_SYSTEM: System prompt for expense classification
    - CLASSIFIER_PARSE: Template for parsing expense text
    - CLASSIFIER_CATEGORIZE: Template for category prediction
    - STRATEGIST_SYSTEM: System prompt for financial advisor role
    - STRATEGIST_PROMPT: Template for recommendation generation
    """
    
    # ==================== CLASSIFIER ====================
    CLASSIFIER_SYSTEM = """You are an expense classification expert.
Analyze the user's expense text and predict its category.

Categories:
- FOOD: Food, groceries, meals, restaurants
- TRANSPORT: Transportation, fuel, taxi
- UTILITIES: Bills (electricity, water, internet)
- ENTERTAINMENT: Entertainment, cinema
- HEALTH: Healthcare, medicine
- EDUCATION: Education, books
- SHOPPING: Shopping, clothing
- HOUSING: Rent, housing
- PERSONAL: Personal care
- OTHER: Other

Return only the category name."""
    
    CLASSIFIER_PARSE = """Analyze this expense text: "{text}"
Format: [DESCRIPTION] [AMOUNT] [TL/₺]

Return in JSON format:
{{"description": "...", "amount": 123.45}}"""
    
    CLASSIFIER_CATEGORIZE = """Which category does this expense belong to?
Description: {description}
Provide only the category name (FOOD, TRANSPORT, etc.)"""
    
    # ==================== STRATEGIST ====================
    STRATEGIST_SYSTEM = """You are an experienced financial advisor.
You help users make informed decisions in budget management.

Your role:
1. Evaluate spending analysis
2. Provide practical recommendations
3. Create action plans
4. Be motivational"""
    
    STRATEGIST_PROMPT = """Financial Status:

📊 Basic Information:
- Total Spending: {total} TL
- Daily Average: {daily} TL
- Monthly Projection: {monthly} TL
- Analysis Period: {days} days

{budget_info}

📁 Category Distribution:
{categories}

📈 Trends:
{trends}

---

Provide to the user:
1. **Status Summary**: 2-3 sentences
2. **Recommendations**: 3-4 practical suggestions
3. **Actions**: To-do items (prioritized)
4. **Goals**: Measurable objectives

Write in English with a friendly and motivating tone."""


def format_budget_info(status: str, income: float = None, remaining: float = None, usage: float = None) -> str:
    """Format budget information section for strategist prompt.
    
    Args:
        status: Budget status (HEALTHY/WARNING/OVER_BUDGET)
        income: Optional monthly income
        remaining: Optional remaining budget
        usage: Optional usage percentage
        
    Returns:
        str: Formatted budget info text with emojis
    """
    if income is None:
        return "💰 Income: Not provided"
    
    emoji = {"HEALTHY": "✅", "WARNING": "⚠️", "OVER_BUDGET": "🔴"}.get(status, "❓")
    lines = [
        f"{emoji} Status: {status}",
        f"💰 Income: {income:.0f} TL",
    ]
    if remaining is not None:
        lines.append(f"💵 Remaining: {remaining:.0f} TL")
    if usage is not None:
        lines.append(f"📊 Usage: {usage:.1f}%")
    return "\n".join(lines)


def format_categories(breakdown: dict) -> str:
    """Format category breakdown section for strategist prompt.
    
    Args:
        breakdown: Dictionary mapping category names to percentages
        
    Returns:
        str: Formatted category list sorted by percentage (highest first)
    """
    if not breakdown:
        return "  (No data)"
    lines = []
    for cat, pct in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  - {cat}: {pct:.1f}%")
    return "\n".join(lines)


def format_trends(trends: list) -> str:
    """Format trends section for strategist prompt.
    
    Args:
        trends: List of trend description strings
        
    Returns:
        str: Formatted trend list or placeholder if empty
    """
    if not trends:
        return "  (Not enough data yet)"
    return "\n".join(f"  - {t}" for t in trends)
