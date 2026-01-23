import streamlit as st
from core.data_loader import load_weekly, load_teams

st.title("📊 Team Analytics")

season = st.sidebar.selectbox("Season", [2024, 2023, 2022])
team = st.sidebar.selectbox("Team", ["KC", "BUF", "PHI", "SF", "DAL"])

wwekly = load_weekly([season])
teams = load_teams()

team_stats = weekly[weekly["team"] == team]

st.subheader(f"{team} — Weekly EPA ({season})")
st.dataframe(team_stats[["week", "epa"]])





