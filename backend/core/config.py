"""
Configuration Management
Simple settings using environment variables.
"""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables.
    
    Provides centralized access to all configuration settings including:
    - Ollama LLM connection and model selection
    - Agent behavior (search, code execution)
    - API server settings
    - Logging configuration
    - Data storage paths
    
    All values have sensible defaults and can be overridden via .env file.
    """
    
    # Ollama
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_fast_model: str = os.getenv("OLLAMA_FAST_MODEL", "llama3.2:3b")
    ollama_accurate_model: str = os.getenv("OLLAMA_ACCURATE_MODEL", "llama3.2:3b")
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    
    # Model Selection
    model_strategy: str = os.getenv("MODEL_STRATEGY", "auto")  # auto, fast, accurate
    
    # Agents
    enable_search_agent: bool = os.getenv("ENABLE_SEARCH_AGENT", "true").lower() == "true"
    search_threshold: float = float(os.getenv("SEARCH_THRESHOLD", "100.0"))
    enable_code_executor: bool = os.getenv("ENABLE_CODE_EXECUTOR", "true").lower() == "true"
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "../data/logs/app.log")
    
    # Storage
    data_dir: Path = Path(os.getenv("DATA_DIR", "../data"))
    expenses_file: Path = Path(os.getenv("EXPENSES_FILE", "../data/expenses.json"))
    analyses_dir: Path = Path(os.getenv("ANALYSES_DIR", "../data/analyses"))
    
    def __post_init__(self):
        """Initialize configuration after dataclass creation.
        
        Creates all required directories for data storage and logging
        if they don't already exist.
        """
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.expenses_file.parent.mkdir(parents=True, exist_ok=True)
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
