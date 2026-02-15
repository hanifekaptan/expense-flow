"""
Search Results Component
"""
import streamlit as st

from utils.formatters import truncate_text


def render_search_results(search_results: list[dict]) -> None:
    """
    Render web search results in an expandable section.
    
    Args:
        search_results: List of search result dictionaries with title, link, snippet
    """
    if not search_results:
        return
    
    with st.expander(f"🔍 Web Araması ({len(search_results)} sonuç)"):
        for idx, result_item in enumerate(search_results, 1):
            title = result_item.get('title', 'Başlık yok')
            link = result_item.get('link', '#')
            snippet = result_item.get('snippet', '')
            snippet_short = truncate_text(snippet, 150)
            
            st.markdown(f"""
            <div class="search-result">
                <strong>{idx}.</strong> <a href="{link}" target="_blank">{title}</a><br>
                <small>{snippet_short}</small>
            </div>
            """, unsafe_allow_html=True)
