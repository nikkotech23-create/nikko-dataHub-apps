import streamlit as st
import pandas as pd
import altair as alt

from core.data_loader import load_pbp, load_schedules, load_teams

st.set_page_config(layout="wide")
st.title("🎮 Game Center")

# Sidebar filters
season = st.sidebar.selectbox("Season", [2024, 2023, 2022], index=0, key="game_season")
week = st.sidebar.selectbox("Week", list(range(1, 19)), index=0)

# Load schedules and teams
schedules = load_schedules([season])
teams_meta = load_teams()

# Filter to selected week
week_games = schedules[schedules["week"] == week].copy()

if week_games.empty:
    st.warning("No games found for this week/season.")
    st.stop()

# Build a nice label for each game
week_games["game_label"] = (
    week_games["away_team"] + " @ " + week_games["home_team"] +
    " — " + week_games["gameday"].astype(str)
)

game_label = st.sidebar.selectbox(
    "Select game",
    week_games["game_label"].tolist()
)

selected_game = week_games[week_games["game_label"] == game_label].iloc[0]
game_id = selected_game["game_id"]

st.subheader(f"{selected_game['away_team']} @ {selected_game['home_team']} — {selected_game['gameday']}")

# Load play-by-play for this season and filter to game
pbp = load_pbp([season])
game_pbp = pbp[pbp["game_id"] == game_id].copy()

if game_pbp.empty:
    st.warning("No play-by-play data available for this game.")
    st.stop()

# Win probability chart (if available)
if "wp" in game_pbp.columns:
    st.markdown("#### Win Probability Over Time")

    wp_df = game_pbp.copy()
    wp_df["play_index"] = range(1, len(wp_df) + 1)

    chart = (
        alt.Chart(wp_df)
        .mark_line()
        .encode(
            x=alt.X("play_index:Q", title="Play Number"),
            y=alt.Y("wp:Q", title="Home Win Probability"),
            color=alt.value("#00E0FF"),
            tooltip=["play_index", "wp", "posteam", "desc"],
        )
        .properties(height=300)
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Win probability data not available for this game.")

# Drive summary
st.markdown("#### Drive Summary")

drive_summary = (
    game_pbp.groupby("drive", as_index=False)
    .agg(
        offense=("posteam", "first"),
        plays=("play_id", "count"),
        drive_start=("game_seconds_remaining", "max"),
        drive_end=("game_seconds_remaining", "min"),
        points=("drive_points", "max"),
        yards=("yards_gained", "sum"),
    )
)

drive_summary["drive_length_sec"] = drive_summary["drive_start"] - drive_summary["drive_end"]

st.dataframe(
    drive_summary[["drive", "offense", "plays", "yards", "points", "drive_length_sec"]],
    use_container_width=True
)

# Play-by-play explorer
st.markdown("#### Play-by-Play Explorer")

cols = ["qtr", "game_seconds_remaining", "posteam", "down", "ydstogo", "yardline_100", "play_type", "yards_gained", "epa", "desc"]
available_cols = [c for c in cols if c in game_pbp.columns]

st.dataframe(
    game_pbp[available_cols],
    use_container_width=True,
    height=400
)


