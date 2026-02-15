"""
Data Formatting Utilities
"""


def format_currency(amount: float, currency: str = "₺") -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: Currency symbol (default: ₺)
        
    Returns:
        str: Formatted currency string (e.g., "₺1,234.56")
    """
    return f"{currency}{amount:,.2f}"


def format_percentage(percentage: float, decimals: int = 1) -> str:
    """
    Format a number as percentage.
    
    Args:
        percentage: The percentage to format
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage string (e.g., "12.3%")
    """
    return f"{percentage:.{decimals}f}%"


def format_time(milliseconds: float) -> str:
    """
    Format processing time.
    
    Args:
        milliseconds: Time in milliseconds
        
    Returns:
        str: Formatted time string (e.g., "1.23s" or "456ms")
    """
    if milliseconds >= 1000:
        seconds = milliseconds / 1000
        return f"{seconds:.2f}s"
    return f"{milliseconds:.0f}ms"


def truncate_text(text: str, max_length: int = 150) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
