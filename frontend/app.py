"""
ExpenseFlow - Streamlit Frontend
Modular architecture with clean separation of concerns.
"""
import streamlit as st

from views import render_home_page
from utils import get_custom_css

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="ExpenseFlow",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== STYLES ====================

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ==================== MAIN ====================

if __name__ == "__main__":
    render_home_page()
