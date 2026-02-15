"""
Base Agent
Abstract base for all agents.
"""
from abc import ABC, abstractmethod
from typing import Any

from loguru import logger


class BaseAgent(ABC):
    """Abstract base class for all agents.
    
    Provides common functionality including:
    - Named logging with agent context
    - Abstract role and execute interface
    - Convenient logging helpers
    
    All concrete agents must implement:
    - role property: Description of agent's responsibility
    - execute method: Main task execution logic
    """
    
    def __init__(self, name: str):
        """Initialize base agent.
        
        Args:
            name: Agent name for logging identification
        """
        self.name = name
        self.logger = logger.bind(agent=name)
    
    @property
    @abstractmethod
    def role(self) -> str:
        """Get agent's role description.
        
        Returns:
            str: Human-readable description of what this agent does
        """
        pass
    
    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's main task.
        
        Args:
            *args: Positional arguments specific to agent
            **kwargs: Keyword arguments specific to agent
            
        Returns:
            Any: Result specific to agent implementation
        """
        pass
    
    def log_start(self, task: str):
        """Log task start with rocket emoji.
        
        Args:
            task: Description of task being started
        """
        self.logger.info(f"🚀 {task}")
    
    def log_complete(self, task: str):
        """Log task completion with checkmark emoji.
        
        Args:
            task: Description of completed task
        """
        self.logger.info(f"✅ {task}")
    
    def log_error(self, task: str, error: Exception):
        """Log error with X emoji.
        
        Args:
            task: Description of failed task
            error: Exception that occurred
        """
        self.logger.error(f"❌ {task}: {error}")
