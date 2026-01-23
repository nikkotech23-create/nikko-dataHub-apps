import streamlit as st
from core.data_loader import load_weekly
from core.metrics import compute_team_epa
from core.visuals import gradient_header, metric_row, epa_heatmap, filter_bar

gradient_header("League Overview", "Standings, efficiency, and league‑wide tendencies.")

filters = filter_bar({
    "Season": [2024, 2023, 2022]
})
season = filters["Season"]

weekly = load_weekly([season])
team_summary = compute_team_epa(weekly)

metric_row([
    ("Avg EPA/play", f"{team_summary['epa_per_play'].mean():+.3f}"),
    ("Avg Success Rate", f"{team_summary['success_rate'].mean():.1%}"),
    ("Total Teams", f"{len(team_summary)}"),
])

st.subheader("Team Efficiency Table")
st.dataframe(team_summary, use_container_width=True)

st.subheader("EPA by Down & Field Position")
pbp = load_pbp([season])
epa_heatmap(pbp, "down", "yardline_100", value="epa", title="EPA by Down & Field Position")
