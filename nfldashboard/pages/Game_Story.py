import streamlit as st
from core.data_loader import load_pbp, load_schedules
from core.metrics import compute_drive_summary, compute_win_prob_series
from core.visuals import gradient_header, win_prob_chart, drive_chart, metric_row

gradient_header("Game Story", "Narrative summary of a single matchup.")

season = st.sidebar.selectbox("Season", [2024, 2023, 2022])
week = st.sidebar.selectbox("Week", list(range(1, 19)))

schedules = load_schedules([season])
week_games = schedules[schedules["week"] == week].copy()

week_games["label"] = week_games["away_team"] + " @ " + week_games["home_team"]
game_label = st.sidebar.selectbox("Game", week_games["label"])
game = week_games[week_games["label"] == game_label].iloc[0]

pbp = load_pbp([season])
game_pbp = pbp[pbp["game_id"] == game["game_id"]].copy()

# Key stats
home = game["home_team"]
away = game["away_team"]
home_points = game_pbp[game_pbp["posteam"] == home]["drive_points"].max()
away_points = game_pbp[game_pbp["posteam"] == away]["drive_points"].max()

metric_row([
    (f"{away} Points", str(int(away_points or 0))),
    (f"{home} Points", str(int(home_points or 0))),
    ("Total Plays", str(len(game_pbp))),
])

# Win prob story
wp = compute_win_prob_series(game_pbp)
if wp is not None:
    st.subheader("Win Probability Story")
    win_prob_chart(wp)

# Drive story
st.subheader("Key Drives")
drives = compute_drive_summary(game_pbp)
top_drives = drives.sort_values("points", ascending=False).head(3)
st.dataframe(top_drives, use_container_width=True)

# Simple textual summary
st.subheader("Narrative Summary")
lead_changes = game_pbp["score_differential"].diff().abs().gt(0).sum() if "score_differential" in game_pbp.columns else "N/A"

st.markdown(
    f"""
    - **Final Score:** {away} {int(away_points or 0)} — {home} {int(home_points or 0)}  
    - **Total Plays:** {len(game_pbp)}  
    - **Lead Changes:** {lead_changes}  
    - **Most Productive Drive:** Drive {int(top_drives.iloc[0]['drive'])} by {top_drives.iloc[0]['offense']}  
    """
)
