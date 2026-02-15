"""
Home View
Main application view for expense analysis.
"""
import asyncio

import httpx
import streamlit as st

from api.client import BudgetAnalystClient
from components import render_analysis_results, render_example_queries, render_expense_input
from components.expense_input import render_settings_sidebar
from utils.formatters import format_time


def render_home_page() -> None:
    """Render the main home page."""
    # Header
    st.markdown('<h1 class="main-header">💰 ExpenseFlow</h1>', unsafe_allow_html=True)
    st.markdown(
        "**Multi-Agent Expense Analysis System** | Powered by 4 AI Agents",
        unsafe_allow_html=True
    )
    
    # Sidebar settings
    income, days_analyzed, enable_search = render_settings_sidebar()
    
    # Health check button in sidebar
    _render_health_check()
    
    # Main content
    render_example_queries()
    expense_input = render_expense_input()
    
    # Analyze button
    if st.button("🚀 Analyze", type="primary", use_container_width=True):
        _handle_analyze(expense_input, income, days_analyzed, enable_search)
    
    # Display results if available
    if "result" in st.session_state:
        render_analysis_results(st.session_state["result"], income)
    
    # Footer
    _render_footer()


def _render_health_check() -> None:
    """Render health check button in sidebar."""
    with st.sidebar:
        st.divider()
        
        if st.button("🏥 Health Check", use_container_width=True):
            with st.spinner("Checking..."):
                try:
                    # Sync wrapper for async call
                    client = BudgetAnalystClient()
                    response = httpx.get(
                        f"{client.base_url}/health",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data["ollama_available"]:
                            st.success("✅ All systems operational")
                        else:
                            st.warning("⚠️ Ollama not available")
                    else:
                        st.error("❌ API error")
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")


def _handle_analyze(
    expense_input: str,
    income: float,
    days_analyzed: int,
    enable_search: bool
) -> None:
    """
    Handle analyze button click.
    
    Args:
        expense_input: User input text
        income: Monthly income
        days_analyzed: Number of days
        enable_search: Whether to enable search
    """
    if not expense_input.strip():
        st.error("❌ Please enter at least one expense")
        return
    
    # Parse expenses
    expense_texts = [
        line.strip()
        for line in expense_input.strip().split("\n")
        if line.strip()
    ]
    
    with st.spinner("🤖 Running multi-agent analysis..."):
        try:
            # Call API (sync wrapper for async)
            response = httpx.post(
                "http://localhost:8000/api/v1/analyze",
                json={
                    "expense_texts": expense_texts,
                    "income": income if income > 0 else None,
                    "days_analyzed": days_analyzed,
                    "enable_search": enable_search,
                },
                timeout=60.0,
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Store in session state
                st.session_state["result"] = result
                
                processing_time = format_time(result['processing_time_ms'])
                st.success(f"✅ Analysis complete in {processing_time}")
                st.rerun()
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.json(response.json())
                
        except Exception as e:
            st.error(f"❌ Error: {e}")


def _render_footer() -> None:
    """Render page footer."""
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <strong>ExpenseFlow v1.0</strong> | 
        Multi-Agent System with Intelligent Model Selection<br>
        Built with FastAPI, Ollama, and Streamlit
    </div>
    """, unsafe_allow_html=True)
