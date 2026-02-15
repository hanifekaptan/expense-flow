# System Architecture

## Overview

ExpenseFlow implements a **clean, modular architecture** inspired by Domain-Driven Design principles, optimized for maintainability and clarity without over-engineering.

## Architectural Principles

### 1. Separation of Concerns
- **Core**: Infrastructure (config, logging, prompts)
- **Domain**: Business entities and logic
- **Services**: Application orchestration
- **API**: External interfaces
- **Agents**: Specialized AI workers

### 2. Single Responsibility
- Each agent handles one specific task
- Each service manages one concern
- Clear boundaries between layers

### 3. Dependency Injection
- Services receive dependencies via constructor
- Easy to test and mock
- Loose coupling

### 4. Async-First
- All I/O operations are async
- Better resource utilization
- Non-blocking execution

## Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│  ┌──────────────────┐     ┌────────────────────┐       │
│  │  Streamlit UI    │     │   FastAPI REST API │       │
│  │  (frontend/)     │────▶│   (api/routes.py)  │       │
│  └──────────────────┘     └────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │           Orchestrator Service                     │ │
│  │  - Coordinates 4-agent pipeline                    │ │
│  │  - Manages workflow execution                      │ │
│  │  - Handles data persistence                        │ │
│  └────────────────────────────────────────────────────┘ │
│                              ↓                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ LLM Service  │  │   Storage    │  │ Search Tool  │ │
│  │ (Ollama)     │  │   Service    │  │ (DuckDuckGo) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              4 Specialized Agents                 │  │
│  │  ┌──────────┐ ┌─────────┐ ┌───────┐ ┌─────────┐ │  │
│  │  │Classifier│ │Searcher │ │Analyst│ │Strategist│ │  │
│  │  └──────────┘ └─────────┘ └───────┘ └─────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────┐         ┌─────────────────────────┐  │
│  │   Models     │         │       Enums             │  │
│  │  - Expense   │         │  - ExpenseCategory      │  │
│  │  - Analysis  │         │  - BudgetStatus         │  │
│  │  - ActionItem│         │  - ActionPriority       │  │
│  └──────────────┘         └─────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Core Module (core/)                 │   │
│  │  - config.py:  Environment configuration         │   │
│  │  - logger.py:  Structured logging                │   │
│  │  - prompts.py: LLM prompt templates              │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Component Deep Dive

### Core Module (`backend/core/`)

**Purpose**: Centralized infrastructure and configuration

**Components**:
- `config.py`: Environment-based configuration using dataclasses
- `logger.py`: Loguru setup with console + file outputs
- `prompts.py`: LLM system prompts and templates

**Design**: 
- Single source of truth for configuration
- No business logic
- Imported by all other modules

---

### Domain Layer (`backend/domain/`)

**Purpose**: Business entities and core logic

**Models** (`models.py`):
```python
@dataclass
class Expense:
    """Expense entity with category and metadata"""
    description: str
    amount: float
    category: ExpenseCategory
    metadata: dict
    id: UUID
    created_at: datetime

@dataclass
class Analysis:
    """Financial analysis with metrics and budget status"""
    total_expenses: float
    daily_rate: float
    monthly_projection: float
    category_breakdown: dict
    budget_status: BudgetStatus
    trends: list[str]
    # ... more fields

@dataclass
class Recommendation:
    """Financial recommendations with action items"""
    summary: str
    recommendations: list[str]
    action_items: list[ActionItem]
    goals: list[Goal]
```

**Enums** (`enums.py`):
- `ExpenseCategory`: 10 categories (FOOD, TRANSPORT, etc.)
- `BudgetStatus`: HEALTHY, WARNING, OVER_BUDGET, UNKNOWN
- `ActionPriority`: LOW, MEDIUM, HIGH, URGENT

---

### Agent Layer (`backend/agents/`)

**Purpose**: Specialized AI workers

**Base Agent** (`base_agent.py`):
```python
class BaseAgent(ABC):
    """Abstract base with logging helpers"""
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Agent role description"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Execute agent's main task"""
        pass
```

**4 Concrete Agents**:

1. **Classifier** (`classifier.py`)
   - Input: Raw expense texts
   - Output: Parsed and categorized Expense objects
   - Strategy: Regex → LLM fallback → Zero-amount fallback

2. **Searcher** (`searcher.py`)
   - Input: List of expenses
   - Output: Enriched expenses with search results
   - Strategy: Search items with amount ≥ 100 TL OR amount = 0.0

3. **Analyst** (`analyst.py`)
   - Input: List of expenses + optional income
   - Output: Analysis with metrics and trends
   - Strategy: Pure calculation, no LLM

4. **Strategist** (`strategist.py`)
   - Input: Analysis object
   - Output: Recommendation with action items and goals
   - Strategy: LLM-generated advice + rule-based actions

---

### Service Layer (`backend/services/`)

**Purpose**: Application orchestration and business services

**Orchestrator** (`orchestrator.py`):
- Coordinates 4-agent pipeline
- Manages workflow execution
- Handles data persistence
- Timing and logging

**LLM Service** (`llm_service.py`):
- Ollama HTTP client
- Intelligent model selection
- Task-type based routing
- Health checking

**Storage Service** (`storage.py`):
- JSON-based persistence
- Async file I/O (aiofiles)
- Expense and analysis storage
- History management

---

### API Layer (`backend/api/`)

**Purpose**: REST API interface

**Routes** (`routes.py`):
```python
@router.get("/health")
async def health_check():
    """Health check endpoint"""

@router.post("/analyze")
async def analyze_expenses(request: AnalyzeRequest):
    """Main analysis endpoint"""

@router.get("/analyses")
async def get_analyses():
    """Get analysis history"""
```

**Schemas** (`schemas.py`):
- Pydantic models for request/response validation
- Type safety and automatic documentation
- OpenAPI schema generation

---

### Tools Layer (`backend/tools/`)

**Purpose**: Utility tools for agents

**Search Tool** (`search_tool.py`):
- DuckDuckGo web search
- Product price research
- Turkish language support

---

## Data Flow

### Complete Analysis Flow

```
1. User Request
   ↓
2. FastAPI receives POST /analyze
   ↓
3. Orchestrator.analyze_expenses()
   ↓
4. Agent 1: Classifier
   - Parse text: "kahve 50 TL" → ("kahve", 50.0)
   - Categorize: "kahve" → FOOD
   - Create: Expense(description="kahve", amount=50.0, category=FOOD)
   ↓
5. Agent 2: Searcher (optional)
   - Filter: expenses with amount ≥ 100 OR amount = 0
   - Search: DuckDuckGo for market prices
   - Enrich: Add search_results to metadata
   ↓
6. Agent 3: Analyst
   - Calculate: total, daily rate, monthly projection
   - Breakdown: spending by category
   - Status: determine HEALTHY/WARNING/OVER_BUDGET
   - Trends: detect high-spending categories
   ↓
7. Agent 4: Strategist
   - Generate: LLM recommendations
   - Create: Prioritized action items
   - Define: Financial goals
   ↓
8. Storage Service
   - Save expenses to data/expenses.json
   - Save analysis to data/analyses/analysis_{id}.json
   ↓
9. Response
   - Return complete analysis + recommendations
   - Include processing time
```

### Model Selection Flow

```
Task Request
   ↓
LLMService.select_model(task_type)
   ↓
   ├─ "classify" → Fast model (llama3.2:1b)
   ├─ "search" → Fast model
   ├─ "analyze" → Fast model
   └─ "recommend" → Accurate model (llama3.2:3b)
   ↓
Ollama HTTP Request
   ↓
Response
```

---

## Key Design Patterns

### 1. Strategy Pattern
- Different model selection strategies (auto/fast/accurate)
- Configurable via environment variables

### 2. Template Method
- BaseAgent defines workflow structure
- Concrete agents implement specific logic

### 3. Facade Pattern
- Orchestrator provides simple interface to complex multi-agent system

### 4. Repository Pattern
- StorageService abstracts data persistence
- Easy to swap JSON with database

### 5. Dependency Injection
- Services injected via constructor
- Testable and mockable

---

## Configuration Management

### Environment Variables

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_FAST_MODEL=llama3.2:1b
OLLAMA_ACCURATE_MODEL=llama3.2:3b
OLLAMA_TIMEOUT=60

# Model Strategy
MODEL_STRATEGY=auto  # auto, fast, accurate

# Agents
ENABLE_SEARCH_AGENT=true
SEARCH_THRESHOLD=100.0

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Storage
DATA_DIR=data
EXPENSES_FILE=data/expenses.json
ANALYSES_DIR=data/analyses

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/app.log
```

---

## Error Handling

### Strategy

1. **Validation Errors**: Caught at API layer (Pydantic)
2. **LLM Errors**: Fallback strategies (regex, zero-amount)
3. **Agent Errors**: Logged but workflow continues where possible
4. **Critical Errors**: Returned as HTTP 500 with error details

### Logging

```python
# Structured logging with loguru
logger.info("Starting analysis")      # Info
logger.debug("Detailed context")      # Debug
logger.warning("Potential issue")     # Warning
logger.error("Error occurred")        # Error
logger.bind(agent="Classifier")       # Contextual
```

---

## Testing Strategy

### Test Coverage

- **Unit Tests**: Individual components (agents, services, tools)
- **Integration Tests**: API endpoints, full workflow
- **Edge Cases**: Invalid inputs, timeouts, concurrent operations
- **Security Tests**: Code executor, input validation

### Test Structure

```
tests/
├── conftest.py           # Fixtures and setup
├── test_agents.py        # Agent unit tests
├── test_models.py        # Domain model tests
├── test_llm_service.py   # LLM service tests
├── test_storage.py       # Storage service tests
├── test_tools.py         # Tool tests
└── test_api_integration.py  # API integration tests
```

---

## Performance & Security

### Optimization Strategies

1. **Async I/O**: Non-blocking file and network operations
2. **Model Selection**: Fast models for simple tasks
3. **Parallel Search**: Multiple searches concurrently
4. **Minimal LLM Calls**: Use regex/rules where possible

### Security Measures

1. **Code Execution**: RestrictedPython sandbox
2. **Input Validation**: Pydantic schemas
3. **No File System Access**: Restricted builtins
4. **Timeout Protection**: All async operations

---

**Last Updated**: February 2026  
**Architecture Version**: 1.0.0
