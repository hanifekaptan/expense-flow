"""
Classifier Agent - Agent 1
Parses and classifies expense texts.
"""
import json
import re

from domain.enums import ExpenseCategory
from domain.models import Expense
from core.prompts import Prompts

from .base_agent import BaseAgent


class ClassifierAgent(BaseAgent):
    """Expense classifier agent (Agent 1).
    
    Parses raw expense text to extract description and amount,
    then categorizes expenses using keyword matching or LLM.
    
    Features:
    - Fast regex parsing with LLM fallback
    - Zero-amount fallback for unparsed prices
    - Keyword-based category classification
    - Handles Turkish and English inputs
    """
    
    def __init__(self, llm_service):
        """Initialize classifier agent.
        
        Args:
            llm_service: LLM service for fallback parsing
        """
        super().__init__("Classifier")
        self.llm = llm_service
    
    @property
    def role(self) -> str:
        return "Parses and categorizes expense texts"
    
    async def execute(self, expense_texts: list[str]) -> list[Expense]:
        """
        Classify multiple expenses.
        
        Args:
            expense_texts: List of expense descriptions
            
        Returns:
            List of Expense entities
        """
        self.log_start(f"Classifying {len(expense_texts)} expenses")
        
        expenses = []
        for text in expense_texts:
            try:
                expense = await self._classify_single(text)
                expenses.append(expense)
            except Exception as e:
                self.log_error(f"classify '{text}'", e)
                continue
        
        self.log_complete(f"Classified {len(expenses)}/{len(expense_texts)}")
        return expenses
    
    async def _classify_single(self, text: str) -> Expense:
        """Classify a single expense text.
        
        Args:
            text: Raw expense text
            
        Returns:
            Expense: Parsed and categorized expense
        """
        # Step 1: Parse (regex first, LLM fallback)
        description, amount = await self._parse(text)
        
        # Step 2: Classify category
        category = await self._categorize(description)
        
        # Step 3: Create entity
        return Expense(
            description=description,
            amount=amount,
            category=category,
        )
    
    async def _parse(self, text: str) -> tuple[str, float]:
        """Parse text to extract description and amount.
        
        Uses regex first for speed, falls back to LLM if needed.
        Returns (text, 0.0) if amount cannot be parsed.
        
        Args:
            text: Raw expense text
            
        Returns:
            tuple: (description, amount) where amount may be 0.0 if unparsed
        """
        # Try regex first (fast) - TL/₺ is now REQUIRED
        # Match last occurrence of number + TL to avoid matching numbers like "16gb"
        pattern = r'^(.+?)\s+(\d+(?:[.,]\d+)?)\s*(TL|₺|tl)\s*$'
        match = re.match(pattern, text.strip(), re.IGNORECASE)
        
        if match:
            description = match.group(1).strip()
            amount_str = match.group(2).replace(',', '.')
            try:
                amount = float(amount_str)
                return description, amount
            except ValueError:
                pass
        
        # Fallback to LLM
        self.logger.debug(f"Regex failed, using LLM for: {text}")
        prompt = Prompts.CLASSIFIER_PARSE.format(text=text)
        response = await self.llm.generate(prompt, task_type="classify", temperature=0.3)
        
        try:
            data = json.loads(response)
            return data["description"], float(data["amount"])
        except (json.JSONDecodeError, KeyError, ValueError):
            # Last fallback: If description looks like a product, mark for search
            # Set amount to 0 so Searcher will know to research it
            self.logger.warning(f"Could not parse amount for: {text}")
            return text, 0.0
    
    async def _categorize(self, description: str) -> ExpenseCategory:
        """Classify expense into a category.
        
        Args:
            description: Expense description
            
        Returns:
            ExpenseCategory: Matched category
        """
        # Try keyword-based first (fast, no LLM)
        category = ExpenseCategory.from_keywords(description)
        
        if category != ExpenseCategory.OTHER:
            return category
        
        # Use LLM for OTHER cases
        self.logger.debug(f"Keyword failed, using LLM for: {description}")
        prompt = Prompts.CLASSIFIER_CATEGORIZE.format(description=description)
        response = await self.llm.generate(
            prompt,
            system=Prompts.CLASSIFIER_SYSTEM,
            task_type="classify",
            temperature=0.3,
        )
        
        category_str = response.upper().strip()
        try:
            return ExpenseCategory(category_str)
        except ValueError:
            return ExpenseCategory.OTHER
