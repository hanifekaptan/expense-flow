"""
Domain Enums
Business logic enumerations.
"""
from enum import Enum


class ExpenseCategory(str, Enum):
    """Expense category enumeration.
    
    Defines all possible expense categories for budget tracking.
    Each category has associated keywords for automatic classification
    and an emoji for UI display.
    """
    
    FOOD = "FOOD"
    TRANSPORT = "TRANSPORT"
    UTILITIES = "UTILITIES"
    ENTERTAINMENT = "ENTERTAINMENT"
    HEALTH = "HEALTH"
    EDUCATION = "EDUCATION"
    SHOPPING = "SHOPPING"
    HOUSING = "HOUSING"
    PERSONAL = "PERSONAL"
    OTHER = "OTHER"
    
    @classmethod
    def from_keywords(cls, text: str) -> "ExpenseCategory":
        """Classify expense text into a category using keyword matching.
        
        Searches for category-specific keywords in the input text.
        Returns the first matching category, or OTHER if no match found.
        
        Args:
            text: Expense description text to classify
            
        Returns:
            ExpenseCategory: Matched category or OTHER as default
            
        Example:
            >>> ExpenseCategory.from_keywords("starbucks coffee")
            ExpenseCategory.FOOD
        """
        text_lower = text.lower()
        
        keywords_map = {
            cls.FOOD: ["market", "yemek", "ekmek", "gıda", "restaurant", "kafe", "kahve", "starbucks", "migros", "carrefour", "a101", "pizza", "dominos"],
            cls.TRANSPORT: ["benzin", "yakıt", "otobüs", "metro", "taksi", "uber", "araç", "uçak", "bilet", "pegasus", "thy", "transfer"],
            cls.UTILITIES: ["elektrik", "su", "gaz", "internet", "telefon", "fatura", "doğalgaz"],
            cls.ENTERTAINMENT: ["sinema", "film", "konser", "tiyatro", "oyun", "netflix", "spotify", "abonel", "disney"],
            cls.HEALTH: ["doktor", "hastane", "eczane", "ilaç", "sağlık"],
            cls.EDUCATION: ["kitap", "kurs", "eğitim", "okul", "ders", "udemy", "coursera"],
            cls.SHOPPING: ["giyim", "kıyafet", "ayakkabı", "alışveriş", "laptop", "bilgisayar", "telefon", "mouse", "klavye", "monitör", "kamera", "kulaklık", "macbook", "iphone", "samsung", "apple", "logitech", "asus", "msi", "lenovo", "dell", "hp", "razer", "keychron", "anker", "teknosa", "vatan", "mediamarkt", "hepsiburada", "trendyol", "amazon", "n11", "gittigidiyor", "usb", "disk", "hard", "ssd", "ram", "ekran", "tablet", "ipad", "airpods", "çanta", "kılıf", "aksesuar", "hub", "adapter", "kablo", "şarj", "powerbank", "trackpad", "webcam", "mikrofon"],
            cls.HOUSING: ["kira", "rent", "ev", "mobilya", "otel", "konaklama", "hilton", "hertz", "kiralama"],
            cls.PERSONAL: ["kuaför", "berber", "güzellik", "spa", "masaj"],
        }
        
        for category, keywords in keywords_map.items():
            if any(kw in text_lower for kw in keywords):
                return category
        
        return cls.OTHER
    
    def get_emoji(self) -> str:
        """Get the emoji representation for this category.
        
        Returns:
            str: Unicode emoji character representing the category
            
        Example:
            >>> ExpenseCategory.FOOD.get_emoji()
            '🍔'
        """
        emoji_map = {
            self.FOOD: "🍔",
            self.TRANSPORT: "🚗",
            self.UTILITIES: "💡",
            self.ENTERTAINMENT: "🎬",
            self.HEALTH: "🏥",
            self.EDUCATION: "📚",
            self.SHOPPING: "🛍️",
            self.HOUSING: "🏠",
            self.PERSONAL: "💇",
            self.OTHER: "📦",
        }
        return emoji_map.get(self, "❓")


class BudgetStatus(str, Enum):
    """Budget health status enumeration.
    
    Represents the financial health of a budget based on spending percentage.
    - GOOD: Under 70% of income spent
    - WARNING: 70-85% of income spent
    - CRITICAL: 85-100% of income spent
    - OVERSPENT: Over 100% of income spent
    """
    
    HEALTHY = "HEALTHY"      # < 80%
    WARNING = "WARNING"       # 80-100%
    OVER_BUDGET = "OVER_BUDGET"  # > 100%
    UNKNOWN = "UNKNOWN"       # No income data
    
    @classmethod
    def from_percentage(cls, percentage: float) -> "BudgetStatus":
        """Determine budget status based on spending percentage.
        
        Args:
            percentage: Spending as percentage of income (0-100+)
            
        Returns:
            BudgetStatus: Health status based on thresholds
            
        Example:
            >>> BudgetStatus.from_percentage(65.5)
            BudgetStatus.GOOD
            >>> BudgetStatus.from_percentage(92.0)
            BudgetStatus.CRITICAL
        """
        if percentage < 0:
            return cls.UNKNOWN
        elif percentage < 80:
            return cls.HEALTHY
        elif percentage <= 100:
            return cls.WARNING
        else:
            return cls.OVER_BUDGET
    
    def get_emoji(self) -> str:
        """Get the emoji representation for this status.
        
        Returns:
            str: Unicode emoji character representing the budget status
        """
        return {
            self.HEALTHY: "✅",
            self.WARNING: "⚠️",
            self.OVER_BUDGET: "🔴",
            self.UNKNOWN: "❓",
        }.get(self, "❓")


class ActionPriority(str, Enum):
    """Action item priority enumeration.
    
    Defines urgency levels for financial action items:
    - LOW: Optional improvements
    - MEDIUM: Should address soon
    - HIGH: Important, take action
    - URGENT: Critical, immediate action required
    """
    
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"
