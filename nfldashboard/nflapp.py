import streamlit as st

st.set_page_config(
  page_title="NFL Analytics Dashboard",
  page_icon="🏈",
  layout="wide"
)

st.title("🏈 NFL Analytics Dashboard")
st.markdown(
    """
    Welcome to the modern NFL analytics hub.  
    Use the sidebar to navigate between league, team, player, and game insights.
    """
)

st.info("Select a page from the sidebar to get started.")


