"""
Logging Configuration
Simple structured logging with loguru.
"""
import sys
from pathlib import Path

from loguru import logger

from core.config import config


def setup_logging():
    """Configure application logging with loguru.
    
    Sets up dual logging outputs:
    - Console: Colored, human-readable format
    - File: Structured format with rotation (10MB, 7 days retention)
    
    Log level and file path are configurable via environment variables.
    """
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True,
    )
    
    # File handler
    log_file = Path(config.log_file)
    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info(f"Logging initialized: level={config.log_level}")


# Export logger
__all__ = ["logger", "setup_logging"]
