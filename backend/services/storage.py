"""
Storage Service
JSON-based data persistence.
"""
import json
from pathlib import Path
from typing import Optional
from uuid import UUID

import aiofiles
from loguru import logger

from core.config import config
from domain.models import Analysis, Expense


class StorageService:
    """JSON-based data persistence layer.
    
    Manages all file I/O for expenses and analyses using async file operations.
    Stores data in simple JSON format for portability and debugging.
    
    Features:
    - Async file operations (aiofiles)
    - Individual analysis files for history tracking
    - Append support for expenses
    - Automatic directory creation
    """
    
    def __init__(self):
        """Initialize storage service.
        
        Creates necessary directories for data persistence.
        """
        self.expenses_file = config.expenses_file
        self.analyses_dir = config.analyses_dir
        
        # Ensure directories exist
        self.expenses_file.parent.mkdir(parents=True, exist_ok=True)
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== EXPENSES ====================
    
    async def save_expenses(self, expenses: list[Expense]) -> None:
        """Save expenses to JSON file (overwrites existing).
        
        Args:
            expenses: List of expense objects to save
        """
        data = [e.to_dict() for e in expenses]
        
        async with aiofiles.open(self.expenses_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        
        logger.info(f"Saved {len(expenses)} expenses to {self.expenses_file}")
    
    async def load_expenses(self) -> list[Expense]:
        """Load expenses from JSON file.
        
        Returns:
            list[Expense]: List of expense objects, empty if file doesn't exist
        """
        if not self.expenses_file.exists():
            return []
        
        try:
            async with aiofiles.open(self.expenses_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                if not content.strip():
                    return []
                data = json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to load expenses: {e}")
            return []
        
        expenses = [Expense.from_dict(d) for d in data]
        logger.info(f"Loaded {len(expenses)} expenses from {self.expenses_file}")
        return expenses
    
    async def append_expenses(self, new_expenses: list[Expense]) -> None:
        """Add new expenses to existing ones.
        
        Args:
            new_expenses: List of new expenses to append
        """
        existing = await self.load_expenses()
        all_expenses = existing + new_expenses
        await self.save_expenses(all_expenses)
    
    # ==================== ANALYSES ====================
    
    async def save_analysis(self, analysis: Analysis) -> str:
        """Save analysis to individual JSON file.
        
        Args:
            analysis: Analysis object to save
            
        Returns:
            str: Analysis ID
        """
        filename = f"analysis_{analysis.id}.json"
        filepath = self.analyses_dir / filename
        
        data = analysis.to_dict()
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        
        logger.info(f"Saved analysis {analysis.id} to {filepath}")
        return str(analysis.id)
    
    async def load_analysis(self, analysis_id: UUID) -> Optional[Analysis]:
        """Load specific analysis by ID.
        
        Args:
            analysis_id: UUID of the analysis to load
            
        Returns:
            Optional[Analysis]: Analysis object or None if not found
        """
        filename = f"analysis_{analysis_id}.json"
        filepath = self.analyses_dir / filename
        
        if not filepath.exists():
            return None
        
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            data = json.loads(content)
        
        return Analysis.from_dict(data)
    
    async def load_all_analyses(self) -> list[Analysis]:
        """Load all saved analyses sorted by creation date (newest first).
        
        Returns:
            list[Analysis]: List of all analyses, empty if none exist
        """
        analyses = []
        
        for filepath in self.analyses_dir.glob("analysis_*.json"):
            try:
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    analyses.append(Analysis.from_dict(data))
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")
                continue
        
        # Sort by created_at descending
        analyses.sort(key=lambda a: a.created_at, reverse=True)
        logger.info(f"Loaded {len(analyses)} analyses")
        return analyses
    
    async def list_analyses(self) -> list[dict]:
        """List all analyses with basic info (id, created_at).
        
        Returns:
            list[dict]: List of analysis summaries
        """
        analyses = []
        
        for filepath in self.analyses_dir.glob("analysis_*.json"):
            try:
                async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    analyses.append({
                        "id": data["id"],
                        "created_at": data["created_at"],
                        "total_expenses": data.get("total_expenses", 0),
                    })
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")
                continue
        
        return analyses
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete specific analysis by ID.
        
        Args:
            analysis_id: UUID string of the analysis to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        filename = f"analysis_{analysis_id}.json"
        filepath = self.analyses_dir / filename
        
        if not filepath.exists():
            return False
        
        try:
            filepath.unlink()
            logger.info(f"Deleted analysis {analysis_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete analysis {analysis_id}: {e}")
            return False
