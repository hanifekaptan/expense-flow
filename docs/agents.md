# Agent System

## Overview

The system uses **4 specialized agents** that work in a coordinated pipeline to analyze expenses and generate recommendations. Each agent has a single responsibility and well-defined input/output contracts.

## Multi-Agent Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                         │
│            Coordinates Multi-Agent Workflow               │
└───────┬──────────┬──────────┬──────────┬─────────────────┘
        │          │          │          │
        ↓          ↓          ↓          ↓
    ┌───────┐  ┌────────┐  ┌───────┐  ┌──────────┐
    │Agent 1│  │Agent 2 │  │Agent 3│  │ Agent 4  │
    │CLASS  │  │SEARCH  │  │ANALYZE│  │STRATEGY  │
    │-IFIER │  │-ER     │  │ -ST   │  │ -ST      │
    └───┬───┘  └────┬───┘  └───┬───┘  └────┬─────┘
        │           │          │           │
        ↓           ↓          ↓           ↓
   [Expenses]   [Metadata]  [Analysis]  [Recommendations]
```

## Agent Pipeline

### Stage 1: Classification
**Agent**: Classifier  
**Input**: Raw expense texts  
**Output**: Parsed and categorized expenses  
**Time**: ~2-3 seconds

### Stage 2: Search (Optional)
**Agent**: Searcher  
**Input**: Classified expenses  
**Output**: Expenses enriched with market data  
**Time**: ~1-2 seconds per item

### Stage 3: Analysis
**Agent**: Analyst  
**Input**: Expenses + optional income  
**Output**: Financial metrics and trends  
**Time**: <1 second

### Stage 4: Strategy
**Agent**: Strategist  
**Input**: Analysis results  
**Output**: Recommendations and action plans  
**Time**: ~5-8 seconds

---

## Agent 1: Classifier

### Purpose
Parses raw expense text and classifies into categories.

### Responsibilities
1. Extract description and amount from text
2. Categorize expense using keywords
3. Handle parsing failures gracefully

### Strategy

**3-Tier Parsing**:
```
1. Regex (Fast)
   ├─ Success? → Return (description, amount)
   └─ Fail? → Try LLM
       ├─ Success? → Return (description, amount)
       └─ Fail? → Return (text, 0.0)  ← Zero-amount fallback
```

### Implementation

```python
class ClassifierAgent(BaseAgent):
    """Expense classifier (Agent 1)"""
    
    async def execute(self, expense_texts: list[str]) -> list[Expense]:
        """Classify multiple expenses"""
        expenses = []
        for text in expense_texts:
            expense = await self._classify_single(text)
            expenses.append(expense)
        return expenses
    
    async def _classify_single(self, text: str) -> Expense:
        """Classify single expense"""
        # Parse: extract description and amount
        description, amount = await self._parse(text)
        
        # Categorize: assign category
        category = await self._categorize(description)
        
        return Expense(description=description, 
                      amount=amount, 
                      category=category)
```

### Parsing Logic

**Regex Pattern**:
```python
pattern = r'^(.+?)\s+(\d+(?:[.,]\d+)?)\s*(TL|₺|tl)\s*$'
# Matches: "kahve 50 TL", "market alışverişi 300.50 TL"
```

**LLM Fallback**:
```python
prompt = """Analyze this expense text: "{text}"
Return in JSON format:
{"description": "...", "amount": 123.45}"""
```

**Zero-Amount Fallback**:
- If both regex and LLM fail to parse amount
- Returns `(text, 0.0)` to trigger Searcher agent
- Example: "laptop" → ("laptop", 0.0)

### Categorization

**Keyword Matching**:
```python
keywords_map = {
    FOOD: ["market", "yemek", "kahve", "restaurant", ...],
    TRANSPORT: ["benzin", "taksi", "uber", "metro", ...],
    SHOPPING: ["laptop", "telefon", "giyim", ...],
    # ... 10 categories total
}
```

**Examples**:
- "starbucks kahve 50 TL" → FOOD
- "uber taksi 120 TL" → TRANSPORT
- "macbook pro" → SHOPPING (zero-amount for Searcher)

### Error Handling
- Invalid text → Logged and skipped
- Parsing failures → Zero-amount fallback
- Category mismatch → Defaults to OTHER

---

## Agent 2: Searcher

### Purpose
Researches market prices for high-value or unparsed expenses via web search.

### Responsibilities
1. Filter expenses that need price research
2. Search DuckDuckGo for market prices
3. Enrich expense metadata with search results

### When to Search

**Criteria**:
```python
searchable = [
    e for e in expenses 
    if e.amount >= threshold OR e.amount == 0.0
]
```

**Examples**:
- `amount >= 100 TL` → High-value item (laptop, rent)
- `amount == 0.0` → Unparsed price (needs research)

### Implementation

```python
class SearcherAgent(BaseAgent):
    """Price searcher (Agent 2)"""
    
    def __init__(self, search_tool, threshold: float = 100.0):
        self.search = search_tool
        self.threshold = threshold
    
    async def execute(self, expenses: list[Expense]) -> list[Expense]:
        """Search for high-value/unparsed expenses"""
        searchable = [
            e for e in expenses 
            if e.amount >= self.threshold or e.amount == 0.0
        ]
        
        for expense in searchable:
            results = await self.search.search_product_price(
                expense.description
            )
            
            if results:
                expense.metadata["search_results"] = results[:3]
                expense.metadata["searched"] = True
        
        return expenses
```

### Search Strategy

**Query Format**:
```python
query = f"{product_name} fiyat"
# Example: "macbook pro fiyat" → Turkish price results
```

**Result Structure**:
```python
{
    "title": "MacBook Pro M2 Fiyatları",
    "link": "https://...",
    "snippet": "MacBook Pro 13-inch M2 chip 8GB RAM..."
}
```

**Metadata Enrichment**:
```python
expense.metadata = {
    "search_results": [
        {"title": "...", "link": "...", "snippet": "..."},
        {"title": "...", "link": "...", "snippet": "..."},
        {"title": "...", "link": "...", "snippet": "..."}
    ],
    "searched": True
}
```

### Performance
- **Parallel Search**: Multiple items searched concurrently
- **Limit Results**: Top 3 results per item
- **Timeout**: 10 seconds per search

---

## Agent 3: Analyst

### Purpose
Calculates financial metrics and determines budget health.

### Responsibilities
1. Calculate total spending, averages, projections
2. Break down spending by category
3. Determine budget status
4. Detect spending trends

### Implementation

```python
class AnalystAgent(BaseAgent):
    """Budget analyst (Agent 3)"""
    
    async def execute(
        self,
        expenses: list[Expense],
        days_analyzed: int,
        income: float = None
    ) -> Analysis:
        """Analyze expenses and generate metrics"""
        
        # Basic calculations
        total = sum(e.amount for e in expenses)
        daily_rate = total / days_analyzed
        monthly_projection = daily_rate * 30
        
        # Category breakdown
        category_totals = {}
        for e in expenses:
            cat = e.category.value
            category_totals[cat] = category_totals.get(cat, 0) + e.amount
        
        # Budget status
        if income:
            usage_pct = (monthly_projection / income) * 100
            status = BudgetStatus.from_percentage(usage_pct)
            remaining = income - monthly_projection
        else:
            status = BudgetStatus.UNKNOWN
            remaining = None
        
        # Trend detection
        trends = self._detect_trends(category_totals, total)
        
        return Analysis(
            total_expenses=total,
            daily_rate=daily_rate,
            monthly_projection=monthly_projection,
            category_breakdown=category_totals,
            budget_status=status,
            remaining_budget=remaining,
            trends=trends
        )
```

### Metrics

**Core Calculations**:
```python
total_spending = sum(expense.amount for expense in expenses)
daily_rate = total_spending / days_analyzed
monthly_projection = daily_rate * 30
```

**Budget Status**:
```python
usage_percentage = (monthly_projection / income) * 100

if usage_percentage < 80:     → HEALTHY
elif usage_percentage <= 100: → WARNING
else:                          → OVER_BUDGET
```

**Category Breakdown**:
```python
{
    "FOOD": 450.0,      # 30% of total
    "TRANSPORT": 300.0, # 20% of total
    "SHOPPING": 750.0,  # 50% of total (HIGH!)
    ...
}
```

### Trend Detection

**Logic**:
```python
def _detect_trends(self, breakdown: dict, total: float) -> list[str]:
    """Detect high-spending categories (≥30%)"""
    trends = []
    for category, amount in breakdown.items():
        percentage = (amount / total) * 100
        if percentage >= 30:
            trends.append(
                f"{emoji} {category} spending is high "
                f"({amount:.0f} TL, {percentage:.1f}%)"
            )
    return trends
```

**Example Output**:
```
🛍️ SHOPPING spending is high (750 TL, 50.0%)
```

### Performance
- **No LLM calls**: Pure calculation
- **Instant**: <100ms execution time
- **No external dependencies**

---

## Agent 4: Strategist

### Purpose
Generates personalized financial recommendations and action plans.

### Responsibilities
1. Generate LLM-based recommendations
2. Create prioritized action items
3. Define financial goals with metrics

### Implementation

```python
class StrategistAgent(BaseAgent):
    """Financial strategist (Agent 4)"""
    
    async def execute(self, analysis: Analysis) -> Recommendation:
        """Generate recommendations"""
        
        # LLM recommendations
        llm_text = await self._generate_llm_recommendations(analysis)
        summary, recommendations = self._parse_response(llm_text)
        
        # Rule-based action items
        actions = self._generate_actions(analysis)
        
        # Financial goals
        goals = self._generate_goals(analysis)
        
        return Recommendation(
            summary=summary,
            recommendations=recommendations,
            action_items=actions,
            goals=goals,
            analysis_id=analysis.id
        )
```

### LLM Recommendations

**Prompt Template**:
```python
"""Financial Status:

📊 Basic Information:
- Total Spending: {total} TL
- Daily Average: {daily} TL
- Monthly Projection: {monthly} TL

✅ Status: {status}
💰 Income: {income} TL
📊 Usage: {usage_pct}%

📁 Category Distribution:
  - FOOD: 30.0%
  - TRANSPORT: 20.0%
  - SHOPPING: 50.0%

📈 Trends:
  - 🛍️ SHOPPING spending is high (750 TL, 50.0%)

---

Provide:
1. Status Summary (2-3 sentences)
2. Recommendations (3-4 suggestions)
3. Actions (prioritized to-dos)
4. Goals (measurable objectives)
"""
```

**Model**: Accurate model (llama3.2:3b) for complex reasoning

### Rule-Based Actions

**Status-Based Priority**:
```python
def _generate_actions(self, analysis: Analysis) -> list[ActionItem]:
    """Generate actions based on budget status"""
    
    actions = []
    status = analysis.budget_status
    
    if status == BudgetStatus.HEALTHY:
        actions.append(ActionItem(
            description="Track your weekly expenses",
            priority=ActionPriority.LOW
        ))
    
    elif status == BudgetStatus.WARNING:
        # Find highest spending category
        top_category = max(analysis.category_breakdown.items(), 
                          key=lambda x: x[1])[0]
        actions.append(ActionItem(
            description=f"Reduce {top_category} spending by 15%",
            priority=ActionPriority.MEDIUM,
            potential_savings=analysis.category_breakdown[top_category] * 0.15
        ))
    
    elif status == BudgetStatus.OVER_BUDGET:
        actions.append(ActionItem(
            description="URGENT: Cut spending by 30%",
            priority=ActionPriority.URGENT
        ))
        actions.append(ActionItem(
            description="Stop all non-essential spending",
            priority=ActionPriority.HIGH
        ))
    
    return actions
```

### Financial Goals

**Goal Structure**:
```python
@dataclass
class Goal:
    description: str         # "Daily spending target"
    current_value: float     # 150.0 (current daily rate)
    target_value: float      # 100.0 (target daily rate)
    timeframe: str          # "7 days"
    category: Optional[str]  # "SHOPPING"
```

**Examples**:
```python
Goal(
    description="Daily spending target",
    current_value=150.0,
    target_value=100.0,
    timeframe="7 days"
)

Goal(
    description="Reduce SHOPPING expenses",
    current_value=750.0,
    target_value=500.0,
    timeframe="30 days",
    category="SHOPPING"
)
```

### Response Parsing

**LLM Output**:
```
Your budget is in WARNING status. You're at 85% usage.

1. Reduce non-essential shopping expenses
2. Set weekly spending limits
3. Track daily expenses in a spreadsheet
4. Find cheaper alternatives for recurring costs
```

**Parsed Result**:
- **Summary**: "Your budget is in WARNING status. You're at 85% usage."
- **Recommendations**: List of 4 bullet points

---

## Base Agent

### Abstract Base Class

```python
class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(agent=name)
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Agent role description"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute agent's main task"""
        pass
    
    def log_start(self, task: str):
        """Log task start"""
        self.logger.info(f"🚀 {task}")
    
    def log_complete(self, task: str):
        """Log task completion"""
        self.logger.info(f"✅ {task}")
    
    def log_error(self, task: str, error: Exception):
        """Log error"""
        self.logger.error(f"❌ {task}: {error}")
```

### Benefits
- Consistent logging across agents
- Template method pattern
- Easy to extend with new agents

---

## Agent Communication

### Data Contracts

**Input/Output Types**:
```python
Classifier:  list[str]      → list[Expense]
Searcher:    list[Expense]  → list[Expense]
Analyst:     list[Expense]  → Analysis
Strategist:  Analysis       → Recommendation
```

### Pipeline Flow

```python
# Orchestrator.analyze_expenses()
expense_texts = ["kahve 50 TL", "laptop", ...]

# Stage 1
expenses = await classifier.execute(expense_texts)
# [Expense(desc="kahve", amount=50, cat=FOOD),
#  Expense(desc="laptop", amount=0, cat=SHOPPING)]

# Stage 2
expenses = await searcher.execute(expenses)
# [Expense(..., metadata={}),
#  Expense(..., metadata={"search_results": [...], "searched": True})]

# Stage 3
analysis = await analyst.execute(expenses, days=7, income=15000)
# Analysis(total=..., status=HEALTHY, trends=[...])

# Stage 4
recommendation = await strategist.execute(analysis)
# Recommendation(summary="...", actions=[...], goals=[...])
```

---

## Performance Summary

| Agent | Time | LLM? | External? |
|-------|------|------|-----------|
| Classifier | 2-3s | ✅ Fast | ❌ |
| Searcher | 1-2s per item | ❌ | ✅ DuckDuckGo |
| Analyst | <1s | ❌ | ❌ |
| Strategist | 5-8s | ✅ Accurate | ❌ |
| **Total** | **10-15s** | 2 calls | Web search |

---

## Error Handling

### Agent-Level
- Each agent logs errors independently
- Failures don't stop the pipeline
- Graceful degradation where possible

### Examples
- Classifier fails → Skip expense
- Searcher fails → Continue without metadata
- Analyst fails → Return error to user
- Strategist fails → Return basic recommendations

---

**Last Updated**: February 2026  
**Agent System Version**: 1.0.0
