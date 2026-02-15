"""
Frontend CSS Styles
"""


def get_custom_css() -> str:
    """
    Get custom CSS for the application.
    
    Returns:
        str: CSS styles as string
    """
    return """
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .expense-item {
            padding: 0.5rem;
            border-left: 4px solid #1f77b4;
            margin: 0.3rem 0;
            background-color: #f9f9f9;
            color: #1e1e1e;
        }
        .action-item {
            padding: 0.5rem;
            margin: 0.3rem 0;
            border-radius: 0.3rem;
            color: #1e1e1e;
        }
        .priority-high {
            border-left: 4px solid #ef4444;
            background-color: #fee;
        }
        .priority-urgent {
            border-left: 4px solid #dc2626;
            background-color: #fee;
            font-weight: bold;
        }
        .priority-medium {
            border-left: 4px solid #f59e0b;
            background-color: #fef3c7;
        }
        .priority-low {
            border-left: 4px solid #10b981;
            background-color: #d1fae5;
        }
        .search-result {
            padding: 0.5rem;
            margin: 0.5rem 0 0.5rem 1rem;
            background-color: #f0f9ff;
            border-left: 3px solid #0ea5e9;
            border-radius: 0.3rem;
            font-size: 0.9rem;
            color: #1e1e1e;
        }
        .search-result a {
            color: #0ea5e9;
            text-decoration: none;
        }
        .search-result a:hover {
            text-decoration: underline;
        }
    </style>
    """
