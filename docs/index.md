# ExpenseFlow - Multi-Agent Budget Analysis System

## Overview

ExpenseFlow is an intelligent expense analysis system powered by a **4-agent architecture** and **local LLM models** (Ollama). It automatically classifies expenses, researches market prices, analyzes spending patterns, and generates personalized financial recommendations.

## Key Features

### 🤖 Multi-Agent Architecture
- **4 specialized agents** working in orchestrated pipeline
- Each agent has single responsibility (SRP)
- Clean separation of concerns

### 🎯 Intelligent Model Selection
- **Task-based model routing**: Fast model for simple tasks, accurate model for complex reasoning
- 3x faster response times for classification and analysis
- Better quality recommendations

### 🔍 Automated Price Research
- **Web search integration** via DuckDuckGo
- Automatically researches high-value items (≥100 TL)
- Handles unparsed prices (amount = 0.0)

### 📊 Financial Analysis
- Category breakdown with percentages
- Daily/monthly spending projections
- Budget status indicators (HEALTHY/WARNING/OVER_BUDGET)
- Trend detection

### 💡 Personalized Recommendations
- LLM-generated financial advice
- Prioritized action items (LOW/MEDIUM/HIGH/URGENT)
- Measurable financial goals
- Category-specific insights

## System Architecture

```
┌──────────────────────────────────────────────┐
│              Frontend (Streamlit)             │
│         User Interface & Visualization        │
└──────────────┬───────────────────────────────┘
               │ HTTP
               ↓
┌──────────────────────────────────────────────┐
│            Backend (FastAPI)                  │
│  ┌────────────────────────────────────────┐  │
│  │        Orchestrator Service            │  │
│  └─────┬──────┬──────┬──────┬────────────┘  │
│        │      │      │      │                 │
│    ┌───▼──┐ ┌▼────┐ ┌▼───┐ ┌▼────────┐      │
│    │Class │ │Search│ │Analy│ │Strategy │      │
│    │-ifier│ │-er   │ │-st  │ │-st      │      │
│    └──────┘ └──────┘ └─────┘ └─────────┘      │
│                                                │
│  ┌──────────┐  ┌─────────┐  ┌──────────┐    │
│  │LLM Service│  │Storage  │  │Tools     │    │
│  │(Ollama)  │  │(JSON)   │  │(Search)  │    │
│  └──────────┘  └─────────┘  └──────────┘    │
└──────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115+
- **LLM**: Ollama (llama3.2:1b, llama3.2:3b)
- **Search**: DuckDuckGo (ddgs)
- **Storage**: JSON-based async file I/O (aiofiles)
- **Logging**: Loguru
- **Security**: RestrictedPython for code execution

### Frontend
- **Framework**: Streamlit
- **HTTP Client**: httpx (async)
- **Visualization**: Plotly

### Infrastructure
- **Python**: 3.11+
- **Local LLM**: Ollama
- **Data Format**: JSON

## Project Structure

```
case-study-2-e/
├── backend/
│   ├── core/                 # Core infrastructure
│   │   ├── config.py        # Configuration management
│   │   ├── logger.py        # Logging setup
│   │   └── prompts.py       # LLM prompt templates
│   ├── agents/              # 4 AI agents
│   │   ├── classifier.py    # Agent 1: Parse & categorize
│   │   ├── searcher.py      # Agent 2: Price research
│   │   ├── analyst.py       # Agent 3: Financial metrics
│   │   └── strategist.py    # Agent 4: Recommendations
│   ├── api/                 # REST API
│   │   ├── routes.py        # Endpoints
│   │   └── schemas.py       # Request/response models
│   ├── domain/              # Business domain
│   │   ├── models.py        # Data entities
│   │   └── enums.py         # Enumerations
│   ├── services/            # Business logic
│   │   ├── orchestrator.py  # Agent coordination
│   │   ├── llm_service.py   # LLM management
│   │   └── storage.py       # Data persistence
│   ├── tools/               # Utility tools
│   │   └── search_tool.py   # Web search
│   ├── tests/               # Test suite (116+ tests)
│   └── main.py             # Application entry
├── frontend/
│   ├── api/                # Backend client
│   ├── components/         # UI components
│   ├── utils/              # Utilities (styles, formatters)
│   ├── views/              # Page views
│   └── app.py              # Streamlit app
├── docs/                   # Documentation
└── data/                   # Data storage
```

## Quick Links

- **[Architecture](architecture.md)** - System design and component details
- **[Agents](agents.md)** - 4-agent pipeline documentation
- **[API](api.md)** - REST API endpoints and schemas
- **[Model Selection](model-selection.md)** - Intelligent LLM routing strategy

## Core Concepts

### Multi-Agent Workflow

The system executes a 4-stage pipeline:

1. **Classifier** → Parses raw text, extracts amounts, categorizes expenses
2. **Searcher** → Researches market prices for high-value or unparsed items
3. **Analyst** → Calculates metrics, determines budget status, detects trends
4. **Strategist** → Generates personalized recommendations and action plans

### Data Flow

```
User Input → Classifier → Searcher → Analyst → Strategist → JSON Response
   ↓            ↓           ↓          ↓          ↓
[Raw Text] [Expenses] [Enriched] [Analysis] [Recommendations]
```

### Key Design Decisions

1. **Local LLM**: Privacy-first, no API costs, full control
2. **Task-Based Model Selection**: Performance optimization
3. **JSON Storage**: Simple, portable, debuggable
4. **Async Architecture**: Better throughput and resource utilization
5. **Modular Frontend**: Clean separation, easy to maintain

## Performance Characteristics

- **Classification**: ~2-3 seconds (fast model)
- **Search**: ~1-2 seconds per item (parallel)
- **Analysis**: <1 second (no LLM, pure calculation)
- **Recommendations**: ~5-8 seconds (accurate model)
- **Total Pipeline**: ~10-15 seconds for 5-10 expenses

## Testing

- **Unit Tests**: 116+ tests covering all components
- **Integration Tests**: API endpoint testing
- **Edge Cases**: Invalid inputs, concurrent operations, security
- **Coverage**: Agents, services, tools, API, domain models

## Documentation Standards

All backend code includes comprehensive English docstrings:
- **Classes**: Purpose, features, attributes
- **Methods**: Args, returns, raises, examples
- **Functions**: Parameters, return values, side effects

## License

MIT License - See LICENSE file for details.

---

**Last Updated**: February 2026  
**Version**: 1.0.0  
**Author**: Case Study 2 - Multi-Agent Budget Analysis
