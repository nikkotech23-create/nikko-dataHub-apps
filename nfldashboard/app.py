import streamlit as st
from core.visuals import gradient_header

st.set_page_config(
    page_title="NFL Analytics Dashboard",
    page_icon="🏈",
    layout="wide"
)

gradient_header(
    "NFL Analytics Dashboard",
    "League, team, player, and game insights with NDH‑grade visuals."
)

st.markdown("Use the sidebar to navigate between pages.")

