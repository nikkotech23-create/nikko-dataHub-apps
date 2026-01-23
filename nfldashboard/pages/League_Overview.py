import streamlit as st
import pandas as pd

st.title("🏟️ League Overview")

st.markdown("High-level view of standings, power rankings, and playoff picture.")

# Sidebar filters (shared pattern)
season = st.sidebar.selectbox("Season", [2024, 2023, 2022], index=0)

# Placeholder standings table
data = {
    "Team": ["KC", "BUF", "PHI", "SF", "DAL"],
    "W": [12, 11, 11, 12, 10],
    "L": [5, 6, 6, 5, 7],
    "ELO": [1650, 1605, 1590, 1665, 1570]
}
df = pd.DataFrame(data)

st.subheader(f"Standings & Power Ratings — {season}")
st.dataframe(df, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("Avg League ELO", "1502")
col2.metric("Top Team ELO", "1665", "+45")
col3.metric("Playoff Locks", "6")


