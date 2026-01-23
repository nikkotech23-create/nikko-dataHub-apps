import streamlit as st
import pandas as pd

from core.data_loader import load_weekly
from core.metrics import compute_qb_metrics, compute_skill_metrics
from core.visuals import (
    gradient_header,
    filter_bar,
    scatter_chart,
    metric_row,
    team_color
)

# -----------------------------
# PAGE HEADER
# -----------------------------
gradient_header(
    "Player Analytics",
    "Efficiency, volume, and performance insights for QBs and skill players."
)

# -----------------------------
# FILTER BAR
# -----------------------------
filters = filter_bar({
    "Season": [2024, 2023, 2022],
    "Position": ["QB", "RB", "WR", "TE"]
})

season = filters["Season"]
position = filters["Position"]

# -----------------------------
# LOAD DATA
# -----------------------------
weekly = load_weekly([season])

# -----------------------------
# METRICS BY POSITION
# -----------------------------
if position == "QB":
    df = compute_qb_metrics(weekly)
    df = df[df["games"] >= 4]  # minimum games filter
    metric_row([
        ("Avg EPA/DB", f"{df['epa_per_dropback'].mean():+.3f}"),
        ("Avg CPOE", f"{df['cpoe'].mean():+.2f}"),
        ("Total QBs", f"{len(df)}"),
    ])
    y_metric = "epa_per_dropback"

else:
    df = compute_skill_metrics(weekly, position)
    df = df[df["games"] >= 4]
    metric_row([
        ("Avg EPA/Touch", f"{df['epa_per_touch'].mean():+.3f}"),
        ("Avg Yards", f"{df['yards'].mean():.1f}"),
        ("Total Players", f"{len(df)}"),
    ])
    y_metric = "epa_per_touch"

# -----------------------------
# PLAYER TABLE
# -----------------------------
st.subheader(f"Top {position}s — {season}")
st.dataframe(
    df.sort_values(y_metric, ascending=False).reset_index(drop=True),
    use_container_width=True
)

# -----------------------------
# SCATTER CHART: VOLUME vs EFFICIENCY
# -----------------------------
st.subheader("Efficiency vs Volume")

if position == "QB":
    scatter_chart(
        df,
        x="yards",
        y="epa_per_dropback",
        color_field="team",
        title="QB Efficiency vs Passing Volume",
        tooltip=["player_name", "team", "yards", "epa_per_dropback", "games"]
    )
else:
    scatter_chart(
        df,
        x="yards",
        y="epa_per_touch",
        color_field="team",
        title=f"{position} Efficiency vs Touches",
        tooltip=["player_name", "team", "yards", "epa_per_touch", "games"]
    )
