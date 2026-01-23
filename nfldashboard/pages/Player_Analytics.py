import streamlit as st
import pandas as pd
import altair as alt

from core.data_loader import load_weekly, load_rosters

st.set_page_config(layout="wide")
st.title("🧍 Player Analytics")

# Sidebar filters
season = st.sidebar.selectbox("Season", [2024, 2023, 2022], index=0, key="player_season")
position = st.sidebar.selectbox("Position", ["QB", "RB", "WR", "TE"], index=0)
min_games = st.sidebar.slider("Minimum games played", 4, 17, 8)

# Load data
weekly = load_weekly([season])
rosters = load_rosters([season])

# Merge weekly stats with roster info
df = weekly.merge(
    rosters[["player_id", "player_name", "position", "team"]],
    on="player_id",
    how="left"
)

# Filter by position and games played
grouped = (
    df[df["position"] == position]
    .groupby(["player_id", "player_name", "team"], as_index=False)
    .agg(
        games=("week", "nunique"),
        epa=("epa", "sum"),
        dropbacks=("dropbacks", "sum"),
        attempts=("attempts", "sum"),
        carries=("carries", "sum"),
        targets=("targets", "sum"),
        yards=("yards", "sum"),
        tds=("td", "sum"),
    )
)

grouped = grouped[grouped["games"] >= min_games]

# Position-specific metrics
if position == "QB":
    grouped["EPA_per_Play"] = grouped["epa"] / (grouped["dropbacks"].replace(0, pd.NA))
    metric_cols = ["games", "epa", "EPA_per_Play", "yards", "tds"]
elif position in ["RB", "WR", "TE"]:
    touches = grouped["carries"].fillna(0) + grouped["targets"].fillna(0)
    grouped["Touches"] = touches
    grouped["EPA_per_Touch"] = grouped["epa"] / touches.replace(0, pd.NA)
    metric_cols = ["games", "Touches", "epa", "EPA_per_Touch", "yards", "tds"]
else:
    metric_cols = ["games", "epa", "yards", "tds"]

st.subheader(f"Top {position}s — {season}")

# Sort by EPA or EPA/play
sort_col = "EPA_per_Play" if "EPA_per_Play" in grouped.columns else "EPA_per_Touch" if "EPA_per_Touch" in grouped.columns else "epa"
grouped = grouped.sort_values(sort_col, ascending=False)

st.dataframe(
    grouped[["player_name", "team"] + metric_cols].reset_index(drop=True),
    use_container_width=True
)

# Chart: EPA vs Yards
if not grouped.empty:
    chart = (
        alt.Chart(grouped)
        .mark_circle(size=80)
        .encode(
            x=alt.X("yards:Q", title="Total Yards"),
            y=alt.Y(sort_col + ":Q", title=sort_col.replace("_", " ")),
            color="team:N",
            tooltip=["player_name", "team", "yards", sort_col, "games"],
        )
        .properties(height=400)
    )
    st.subheader("Efficiency vs Volume")
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("No players match the current filters.")
