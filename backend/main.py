"""
ExpenseFlow API
FastAPI application with multi-agent system.
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import init_services, router
from core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize services (LLM, storage, agents)
    - Shutdown: Cleanup resources
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("🚀 Starting ExpenseFlow API")
    init_services()
    logger.info("✅ Services initialized")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down ExpenseFlow API")


# Create FastAPI app
app = FastAPI(
    title="ExpenseFlow API",
    description="Multi-Agent Budget Analysis System with Intelligent Model Selection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/v1", tags=["analysis"])


@app.get("/")
async def root():
    """Root endpoint providing API information.
    
    Returns:
        dict: API metadata including name, version, agents, features
    """
    return {
        "name": "ExpenseFlow API",
        "version": "1.0.0",
        "agents": ["Classifier", "Searcher", "Analyst", "Strategist"],
        "features": [
            "Multi-agent workflow",
            "Intelligent model selection",
            "Web search integration",
            "Safe code execution",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level="debug" if config.debug else "info",
    )
