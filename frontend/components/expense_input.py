"""
Expense Input Component
"""
import streamlit as st


def render_expense_input() -> str:
    """
    Render expense input form.
    
    Returns:
        str: User input text (one expense per line)
    """
    st.header("📝 Enter Expenses")
    st.markdown(
        "Enter one expense per line (e.g., `starbucks kahve 85 TL`, "
        "`migros market alışverişi 450 TL`)"
    )
    
    expense_input = st.text_area(
        "Expense List",
        height=200,
        value=st.session_state.get("example_query", ""),
        placeholder=(
            "starbucks kahve 85 TL\n"
            "migros market alışverişi 450 TL\n"
            "asus laptop 15600 TL\n"
            "uber kadıköy-beşiktaş 180 TL"
        ),
        label_visibility="collapsed",
        key="expense_input_area"
    )
    
    return expense_input


def render_settings_sidebar() -> tuple[float, int, bool]:
    """
    Render settings in sidebar.
    
    Returns:
        tuple: (income, days_analyzed, enable_search)
    """
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Income input
        income = st.number_input(
            "Monthly Income (TL)",
            min_value=0.0,
            value=15000.0,
            step=1000.0,
            help="Your monthly income for budget comparison"
        )
        
        # Days analyzed
        days_analyzed = st.number_input(
            "Days Analyzed",
            min_value=1,
            max_value=365,
            value=7,
            step=1,
            help="Number of days covered by your expenses"
        )
        
        # Enable search
        enable_search = st.checkbox(
            "Enable Web Search",
            value=True,
            help="Search for product prices online (for items >100 TL)"
        )
        
        st.divider()
        
        # Info
        st.subheader("🤖 Active Agents")
        st.markdown("""
        1. **Classifier** - Parse & categorize
        2. **Searcher** - Research prices
        3. **Analyst** - Calculate metrics
        4. **Strategist** - Generate advice
        """)
        
        return income, days_analyzed, enable_search
