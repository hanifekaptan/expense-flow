"""
LLM Service
Ollama client with intelligent model selection.
"""
from typing import Literal

import httpx
from loguru import logger

from core.config import config


class LLMService:
    """LLM service with intelligent model selection strategy.
    
    Manages communication with Ollama LLM and implements smart model selection
    based on task complexity. Can use different models for different tasks to
    balance speed and accuracy.
    
    Key Features:
    - Auto/fast/accurate model selection strategies  
    - Task-type based model routing
    - Async HTTP communication with Ollama
    - Configurable timeout and temperature
    - Health checking
    """
    
    def __init__(self):
        """Initialize LLM service with configuration from config.
        
        Loads Ollama connection settings, model names, and selection strategy.
        """
        self.base_url = config.ollama_base_url
        self.fast_model = config.ollama_fast_model
        self.accurate_model = config.ollama_accurate_model
        self.timeout = config.ollama_timeout
        self.strategy = config.model_strategy
        
        self._client = None
    
    async def __aenter__(self):
        """Async context manager entry.
        
        Creates HTTP client for connection pooling.
        
        Returns:
            self: Service instance for context manager
        """
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout)
        )
        return self
    
    async def __aexit__(self, *args):
        """Async context manager exit.
        
        Closes HTTP client and releases resources.
        """
        if self._client:
            await self._client.aclose()
    
    def select_model(
        self,
        task_type: Literal["classify", "analyze", "recommend", "search", "general"] = "general"
    ) -> str:
        """
        🔑 MODEL SELECTION STRATEGY (Core Feature!)
        
        Intelligently selects model based on task characteristics.
        
        Strategy:
        - classify: Fast model (simple parsing)
        - search: Fast model (query generation)
        - analyze: Fast model (mostly calculations)
        - recommend: Accurate model (complex reasoning)
        - general: Based on strategy setting
        
        Args:
            task_type: Type of task
            
        Returns:
            Model name to use
        """
        # Force strategy
        if self.strategy == "fast":
            return self.fast_model
        if self.strategy == "accurate":
            return self.accurate_model
        
        # Auto strategy (intelligent selection)
        if task_type in ["classify", "search", "analyze"]:
            model = self.fast_model
        elif task_type == "recommend":
            model = self.accurate_model
        else:
            model = self.fast_model  # Default to fast for better UX
        
        logger.debug(f"Model selection: task={task_type} → {model}")
        return model
    
    async def generate(
        self,
        prompt: str,
        system: str = None,
        task_type: str = "general",
        temperature: float = 0.7,
        max_tokens: int = None,
    ) -> str:
        """
        Generate completion from Ollama.
        
        Args:
            prompt: User prompt
            system: System prompt
            task_type: Task type for model selection
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Generated text
        """
        # Select model based on task
        model = self.select_model(task_type)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        }
        
        if system:
            payload["system"] = system
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        logger.debug(f"Generating: model={model}, task={task_type}")
        
        try:
            if not self._client:
                # Create temporary client if not in context manager
                async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                    response = await client.post("/api/generate", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("response", "").strip()
            else:
                response = await self._client.post("/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
        
        except httpx.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            raise RuntimeError(f"LLM error: {e}")
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise RuntimeError(f"LLM error: {e}")
    
    async def check_health(self) -> bool:
        """Check if Ollama service is accessible.
        
        Returns:
            bool: True if Ollama is reachable, False otherwise
        """
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=5.0) as client:
                response = await client.get("/")
                return response.status_code == 200
        except Exception:
            return False
