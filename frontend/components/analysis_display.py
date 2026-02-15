"""
Analysis Results Display Component
"""
from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.search_results import render_search_results
from utils.formatters import format_currency, format_percentage


def render_analysis_results(result: dict[str, Any], income: float) -> None:
    """
    Render complete analysis results with tabs.
    
    Args:
        result: Analysis result dictionary from API
        income: User's monthly income
    """
    st.divider()
    st.header("📊 Analysis Results")
    
    # Top metrics
    _render_metrics(result, income)
    
    # Tabbed content
    tab1, tab2, tab3, tab4 = st.tabs([
        "💳 Expenses",
        "📈 Charts",
        "💡 Recommendations",
        "🔍 Insights"
    ])
    
    with tab1:
        _render_expenses_tab(result)
    
    with tab2:
        _render_charts_tab(result)
    
    with tab3:
        _render_recommendations_tab(result)
    
    with tab4:
        _render_insights_tab(result)


def _render_metrics(result: dict[str, Any], income: float) -> None:
    """Render top-level metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    analysis = result['analysis']
    
    with col1:
        st.metric(
            "Total Spent",
            format_currency(analysis['total_spent']),
        )
    
    with col2:
        st.metric(
            "Daily Rate",
            format_currency(analysis['daily_rate']),
        )
    
    with col3:
        st.metric(
            "Monthly Projection",
            format_currency(analysis['monthly_projection']),
        )
    
    with col4:
        budget_pct = analysis['budget_percentage']
        st.metric(
            "Budget Usage",
            format_percentage(budget_pct),
            delta=format_percentage(budget_pct - 100) if income > 0 else None,
            delta_color="inverse",
        )


def _render_expenses_tab(result: dict[str, Any]) -> None:
    """Render expenses tab with search results."""
    st.subheader("Expense Details")
    
    for expense in result['expenses']:
        # Main expense info
        st.markdown(f"""
        <div class="expense-item">
            <strong>{expense['text']}</strong><br>
            Amount: {format_currency(expense['amount'])} | Category: {expense['category']}
        </div>
        """, unsafe_allow_html=True)
        
        # Search results if available
        search_results = expense.get('metadata', {}).get('search_results', [])
        if search_results:
            render_search_results(search_results)


def _render_charts_tab(result: dict[str, Any]) -> None:
    """Render charts tab with visualizations."""
    st.subheader("Category Breakdown")
    
    breakdown = result['analysis']['category_breakdown']
    
    # Pie chart
    fig = px.pie(
        values=list(breakdown.values()),
        names=list(breakdown.keys()),
        title="Spending by Category",
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Bar chart
    fig2 = go.Figure(data=[
        go.Bar(
            x=list(breakdown.keys()),
            y=list(breakdown.values()),
            text=[format_currency(v) for v in breakdown.values()],
            textposition="outside",
        )
    ])
    fig2.update_layout(
        title="Category Totals",
        xaxis_title="Category",
        yaxis_title="Amount (TL)",
    )
    st.plotly_chart(fig2, use_container_width=True)


def _render_recommendations_tab(result: dict[str, Any]) -> None:
    """Render recommendations tab with actions and goals."""
    st.subheader("Strategic Recommendations")
    
    recommendation = result['recommendation']
    
    # Summary
    st.info(recommendation['summary'])
    
    # Actions
    st.markdown("### 🎯 Action Items")
    
    for action in recommendation['actions']:
        priority = action['priority'].lower()
        priority_class = f"priority-{priority}"
        
        savings_text = ""
        if action.get('potential_savings'):
            savings_text = f"<br>💰 Potential Savings: {format_currency(action['potential_savings'])}"
        
        st.markdown(f"""
        <div class="action-item {priority_class}">
            <strong>[{action['priority']}]</strong> {action['description']}
            {savings_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Goals
    if recommendation['goals']:
        st.markdown("### 🎯 Financial Goals")
        for goal in recommendation['goals']:
            current = goal['current_value']
            target = goal['target_value']
            difference = current - target
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{goal['description']}**")
                st.caption(f"Zaman: {goal['timeframe']}")
            with col2:
                st.metric("Mevcut", format_currency(current))
            with col3:
                st.metric(
                    "Hedef",
                    format_currency(target),
                    delta=f"-{format_currency(difference)}",
                    delta_color="normal"
                )


def _render_insights_tab(result: dict[str, Any]) -> None:
    """Render insights tab with budget status."""
    st.subheader("Budget Insights")
    
    analysis = result['analysis']
    
    for insight in analysis['insights']:
        st.markdown(f"- {insight}")
    
    # Budget status
    status = analysis['budget_status']
    if status == "HEALTHY":
        st.success("✅ Budget Status: Healthy")
    elif status == "WARNING":
        st.warning("⚠️ Budget Status: Warning")
    else:
        st.error("❌ Budget Status: Critical")
