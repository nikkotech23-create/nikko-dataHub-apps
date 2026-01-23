# core/metrics.py

import pandas as pd
import numpy as np

# -----------------------------
# TEAM‑LEVEL METRICS
# -----------------------------

def compute_team_epa(weekly_df):
    """Return EPA/play and success rate for each team."""
    df = weekly_df.copy()

    df["plays"] = df["attempts"].fillna(0) + df["carries"].fillna(0)
    df["epa_per_play"] = df["epa"] / df["plays"].replace(0, pd.NA)
    df["success_rate"] = df["success"].fillna(0) / df["plays"].replace(0, pd.NA)

    team_summary = (
        df.groupby("team", as_index=False)
        .agg(
            games=("week", "nunique"),
            plays=("plays", "sum"),
            epa=("epa", "sum"),
            epa_per_play=("epa_per_play", "mean"),
            success_rate=("success_rate", "mean"),
            yards=("yards", "sum"),
            tds=("td", "sum"),
        )
    )

    return team_summary


# -----------------------------
# PLAYER‑LEVEL METRICS
# -----------------------------

def compute_qb_metrics(weekly_df):
    """Return QB efficiency metrics."""
    df = weekly_df.copy()
    df = df[df["position"] == "QB"]

    grouped = (
        df.groupby(["player_id", "player_name", "team"], as_index=False)
        .agg(
            games=("week", "nunique"),
            dropbacks=("dropbacks", "sum"),
            epa=("epa", "sum"),
            cpoe=("cpoe", "mean"),
            yards=("yards", "sum"),
            tds=("td", "sum"),
        )
    )

    grouped["epa_per_dropback"] = grouped["epa"] / grouped["dropbacks"].replace(0, pd.NA)

    return grouped


def compute_skill_metrics(weekly_df, position):
    """Return RB/WR/TE metrics."""
    df = weekly_df.copy()
    df = df[df["position"] == position]

    grouped = (
        df.groupby(["player_id", "player_name", "team"], as_index=False)
        .agg(
            games=("week", "nunique"),
            carries=("carries", "sum"),
            targets=("targets", "sum"),
            epa=("epa", "sum"),
            yards=("yards", "sum"),
            tds=("td", "sum"),
        )
    )

    grouped["touches"] = grouped["carries"].fillna(0) + grouped["targets"].fillna(0)
    grouped["epa_per_touch"] = grouped["epa"] / grouped["touches"].replace(0, pd.NA)

    return grouped


# -----------------------------
# GAME‑LEVEL METRICS
# -----------------------------

def compute_drive_summary(pbp_df):
    """Summaries for each drive in a game."""
    df = pbp_df.copy()

    summary = (
        df.groupby("drive", as_index=False)
        .agg(
            offense=("posteam", "first"),
            plays=("play_id", "count"),
            yards=("yards_gained", "sum"),
            points=("drive_points", "max"),
            start=("game_seconds_remaining", "max"),
            end=("game_seconds_remaining", "min"),
        )
    )

    summary["drive_length_sec"] = summary["start"] - summary["end"]

    return summary


def compute_win_prob_series(pbp_df):
    """Return win probability time series if available."""
    df = pbp_df.copy()

    if "wp" not in df.columns:
        return None

    df["play_index"] = range(1, len(df) + 1)
    return df[["play_index", "wp", "posteam", "desc"]]


