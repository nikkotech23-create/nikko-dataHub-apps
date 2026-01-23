import streamlit as st
from core.data_loader import load_weekly, load_pbp
from core.metrics import compute_team_epa
from core.visuals import gradient_header, metric_row, line_chart, team_color, filter_bar

gradient_header("Team Analytics", "Deep‑dive into team efficiency and tendencies.")

filters = filter_bar({
    "Season": [2024, 2023, 2022],
    "Team": ["KC", "BUF", "PHI", "SF", "DAL"]
})
season = filters["Season"]
team = filters["Team"]

weekly = load_weekly([season])
team_summary = compute_team_epa(weekly)
row = team_summary[team_summary["team"] == team].iloc[0]

metric_row([
    ("EPA/play", f"{row['epa_per_play']:+.3f}"),
    ("Success Rate", f"{row['success_rate']:.1%}"),
    ("Total Plays", f"{int(row['plays'])}"),
])

pbp = load_pbp([season])
team_pbp = pbp[pbp["posteam"] == team].copy()
team_pbp["Week"] = team_pbp["week"]

line_chart(
    team_pbp.groupby("Week", as_index=False)["epa"].mean(),
    "Week",
    "epa",
    title=f"{team} EPA by Week",
    color=team_color(team)
)





