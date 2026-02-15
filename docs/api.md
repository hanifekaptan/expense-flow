# API Documentation

## Overview

ExpenseFlow exposes a RESTful API built with FastAPI. The API provides endpoints for health checking, expense analysis, and history retrieval.

**Base URL**: `http://localhost:8000/api/v1`

## Endpoints

### Health Check

**GET** `/health`

Check API and Ollama service health.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "ollama_available": true,
  "timestamp": "2026-02-15T00:13:45.123456"
}
```

**Status Values**:
- `healthy`: All services operational
- `degraded`: API running but Ollama unavailable
- `unhealthy`: Critical failure

**Example**:
```bash
curl http://localhost:8000/api/v1/health
```

---

### Analyze Expenses

**POST** `/analyze`

Execute multi-agent workflow to analyze expenses.

**Request Body**:
```json
{
  "expense_texts": [
    "kahve 50 TL",
    "market alışverişi 300 TL",
    "laptop"
  ],
  "income": 15000.0,
  "days_analyzed": 7,
  "enable_search": true
}
```

**Request Schema**:
```python
class AnalyzeRequest(BaseModel):
    expense_texts: list[str]  # Required, min 1 item
    income: Optional[float] = None  # Optional monthly income
    days_analyzed: int = 1  # 1-365 days
    enable_search: bool = True  # Enable web search
```

**Response** (200 OK):
```json
{
  "expenses": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "kahve",
      "amount": 50.0,
      "category": "FOOD",
      "metadata": {}
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "text": "market alışverişi",
      "amount": 300.0,
      "category": "FOOD",
      "metadata": {}
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "text": "laptop",
      "amount": 0.0,
      "category": "SHOPPING",
      "metadata": {
        "search_results": [
          {
            "title": "MacBook Pro Fiyatları 2026",
            "link": "https://...",
            "snippet": "MacBook Pro 13-inch M2..."
          }
        ],
        "searched": true
      }
    }
  ],
  "analysis": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "total_spent": 350.0,
    "daily_rate": 50.0,
    "monthly_projection": 1500.0,
    "category_breakdown": {
      "FOOD": 350.0,
      "SHOPPING": 0.0
    },
    "budget_status": "HEALTHY",
    "budget_percentage": 10.0,
    "insights": [
      "🍔 FOOD spending is high (350 TL, 100.0%)"
    ],
    "created_at": "2026-02-15T00:15:30.123456"
  },
  "recommendation": {
    "summary": "Your budget is healthy. Continue tracking expenses.",
    "actions": [
      {
        "description": "Track your weekly expenses",
        "priority": "LOW",
        "potential_savings": null
      }
    ],
    "goals": [
      {
        "description": "Daily spending target",
        "current_value": 50.0,
        "target_value": 45.0,
        "timeframe": "7 days"
      }
    ]
  },
  "processing_time_ms": 12345.67
}
```

**Response Schema**:
```python
class AnalyzeResponse(BaseModel):
    expenses: list[ExpenseResponse]
    analysis: AnalysisResponse
    recommendation: RecommendationResponse
    processing_time_ms: float
```

**Error Responses**:

**400 Bad Request** - Invalid input:
```json
{
  "detail": [
    {
      "loc": ["body", "expense_texts"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error** - Processing error:
```json
{
  "detail": "Analysis failed: No expenses were successfully classified"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "expense_texts": ["kahve 50 TL", "market 300 TL"],
    "income": 15000,
    "days_analyzed": 7,
    "enable_search": true
  }'
```

---

### Get Analysis History

**GET** `/analyses`

Retrieve all past analyses sorted by creation date (newest first).

**Response** (200 OK):
```json
{
  "analyses": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "total_spent": 350.0,
      "daily_rate": 50.0,
      "monthly_projection": 1500.0,
      "category_breakdown": {
        "FOOD": 350.0
      },
      "budget_status": "HEALTHY",
      "budget_percentage": 10.0,
      "insights": [],
      "created_at": "2026-02-15T00:15:30.123456"
    }
  ],
  "total": 1
}
```

**Response Schema**:
```python
class AnalysisListResponse(BaseModel):
    analyses: list[AnalysisResponse]
    total: int
```

**Example**:
```bash
curl http://localhost:8000/api/v1/analyses
```

---

## Data Models

### ExpenseResponse

```python
class ExpenseResponse(BaseModel):
    """Single expense response"""
    id: UUID
    text: str
    amount: float
    category: str  # ExpenseCategory enum value
    metadata: dict
```

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "kahve",
  "amount": 50.0,
  "category": "FOOD",
  "metadata": {
    "searched": false
  }
}
```

---

### AnalysisResponse

```python
class AnalysisResponse(BaseModel):
    """Financial analysis response"""
    id: UUID
    total_spent: float
    daily_rate: float
    monthly_projection: float
    category_breakdown: dict[str, float]
    budget_status: str  # BudgetStatus enum value
    budget_percentage: float
    insights: list[str]
    created_at: datetime
```

**Example**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "total_spent": 1500.0,
  "daily_rate": 214.29,
  "monthly_projection": 6428.7,
  "category_breakdown": {
    "FOOD": 450.0,
    "TRANSPORT": 300.0,
    "SHOPPING": 750.0
  },
  "budget_status": "HEALTHY",
  "budget_percentage": 42.86,
  "insights": [
    "🛍️ SHOPPING spending is high (750 TL, 50.0%)"
  ],
  "created_at": "2026-02-15T00:15:30.123456"
}
```

---

### ActionItemResponse

```python
class ActionItemResponse(BaseModel):
    """Action item response"""
    description: str
    priority: str  # ActionPriority enum value
    potential_savings: Optional[float]
```

**Example**:
```json
{
  "description": "Reduce SHOPPING spending by 15%",
  "priority": "MEDIUM",
  "potential_savings": 112.5
}
```

**Priority Values**:
- `LOW`: Optional improvements
- `MEDIUM`: Should address soon
- `HIGH`: Important, take action
- `URGENT`: Critical, immediate action required

---

### GoalResponse

```python
class GoalResponse(BaseModel):
    """Financial goal response"""
    description: str
    current_value: float
    target_value: float
    timeframe: str
```

**Example**:
```json
{
  "description": "Daily spending target",
  "current_value": 214.29,
  "target_value": 150.0,
  "timeframe": "7 days"
}
```

---

### RecommendationResponse

```python
class RecommendationResponse(BaseModel):
    """Financial recommendations"""
    summary: str
    actions: list[ActionItemResponse]
    goals: list[GoalResponse]
```

**Example**:
```json
{
  "summary": "Your budget is in WARNING status. Consider reducing expenses.",
  "actions": [
    {
      "description": "Reduce SHOPPING spending by 15%",
      "priority": "MEDIUM",
      "potential_savings": 112.5
    }
  ],
  "goals": [
    {
      "description": "Daily spending target",
      "current_value": 214.29,
      "target_value": 150.0,
      "timeframe": "7 days"
    }
  ]
}
```

---

## Enumerations

### ExpenseCategory

Categories for expense classification:

```python
class ExpenseCategory(str, Enum):
    FOOD = "FOOD"              # 🍔 Food, groceries, restaurants
    TRANSPORT = "TRANSPORT"    # 🚗 Transportation, fuel, taxi
    UTILITIES = "UTILITIES"    # 💡 Bills, electricity, internet
    ENTERTAINMENT = "ENTERTAINMENT"  # 🎬 Movies, entertainment
    HEALTH = "HEALTH"          # 🏥 Healthcare, medicine
    EDUCATION = "EDUCATION"    # 📚 Education, books, courses
    SHOPPING = "SHOPPING"      # 🛍️ Shopping, electronics, clothing
    HOUSING = "HOUSING"        # 🏠 Rent, housing costs
    PERSONAL = "PERSONAL"      # 💇 Personal care, beauty
    OTHER = "OTHER"            # 📦 Uncategorized
```

### BudgetStatus

Budget health indicators:

```python
class BudgetStatus(str, Enum):
    HEALTHY = "HEALTHY"        # ✅ < 80% of income spent
    WARNING = "WARNING"        # ⚠️ 80-100% of income spent
    OVER_BUDGET = "OVER_BUDGET"  # 🔴 > 100% of income spent
    UNKNOWN = "UNKNOWN"        # ❓ No income provided
```

### ActionPriority

Action urgency levels:

```python
class ActionPriority(str, Enum):
    LOW = "LOW"        # Optional improvements
    MEDIUM = "MEDIUM"  # Should address soon
    HIGH = "HIGH"      # Important, take action
    URGENT = "URGENT"  # Critical, immediate action
```

---

## Error Handling

### Validation Errors (400)

Pydantic validation errors are automatically formatted:

```json
{
  "detail": [
    {
      "loc": ["body", "days_analyzed"],
      "msg": "ensure this value is less than or equal to 365",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### Processing Errors (500)

Application errors return structured messages:

```json
{
  "detail": "Analysis failed: [specific error message]"
}
```

**Common Errors**:
- No expenses classified successfully
- Ollama service unavailable
- LLM generation timeout
- Invalid expense format

---

## Rate Limiting

Currently no rate limiting implemented. Recommended for production:
- 60 requests per minute per IP
- 10 analysis requests per minute per user

---

## CORS Configuration

**Development**:
```python
allow_origins=["*"]  # All origins allowed
```

**Production** (recommended):
```python
allow_origins=[
    "http://localhost:8501",  # Streamlit frontend
    "https://yourdomain.com"
]
```

---

## OpenAPI Documentation

Interactive API documentation available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## Performance Characteristics

| Endpoint | Avg Time | Max Time | Notes |
|----------|----------|----------|-------|
| `/health` | 50ms | 200ms | Depends on Ollama ping |
| `/analyze` | 10-15s | 30s | 5-10 expenses with search |
| `/analyses` | 100ms | 500ms | Depends on history size |

**Bottlenecks**:
- LLM generation (5-8s for recommendations)
- Web search (1-2s per item)
- Classification (2-3s total)

---

## Client Examples

### Python (httpx)

```python
import httpx

async with httpx.AsyncClient() as client:
    # Analyze expenses
    response = await client.post(
        "http://localhost:8000/api/v1/analyze",
        json={
            "expense_texts": ["kahve 50 TL", "market 300 TL"],
            "income": 15000,
            "days_analyzed": 7,
            "enable_search": True
        }
    )
    result = response.json()
    print(f"Total spent: {result['analysis']['total_spent']} TL")
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    expense_texts: ['kahve 50 TL', 'market 300 TL'],
    income: 15000,
    days_analyzed: 7,
    enable_search: true
  })
});

const result = await response.json();
console.log(`Total spent: ${result.analysis.total_spent} TL`);
```

### cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Analyze
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "expense_texts": ["kahve 50 TL"],
    "income": 15000,
    "days_analyzed": 7
  }'

# Get history
curl http://localhost:8000/api/v1/analyses
```

---

## Authentication

**Current**: No authentication  
**Production**: Consider implementing:
- API keys
- JWT tokens
- OAuth 2.0

---

## Versioning

API uses URL versioning:
- Current: `/api/v1`
- Future: `/api/v2` (breaking changes)

---

**Last Updated**: February 2026  
**API Version**: 1.0.0
