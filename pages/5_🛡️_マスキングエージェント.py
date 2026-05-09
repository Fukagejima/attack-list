"""
SharePoint マスキングエージェント ページ
"""
import streamlit as st

st.set_page_config(
    page_title="マスキングエージェント",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views.masking_agent import render

render()
