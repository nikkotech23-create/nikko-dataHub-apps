# core/visuals.py

import streamlit as st
import altair as alt
import pandas as pd

def gradient_header(title, subtitle=None):
    st.markdown(
        f"""
        <div style="
            padding: 32px 24px;
            border-radius: 16px;
            background: linear-gradient(135deg, #0A0F24 0%, #111C44 40%, #1A2A6C 100%);
            border: 1px solid rgba(0, 224, 255, 0.25);
            box-shadow: 0 0 25px rgba(0, 224, 255, 0.15);
        ">
            <h1 style="color:#00E0FF; margin-bottom:0;">{title}</h1>
            {f'<p style="color:#D1D5DB; margin-top:8px;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

TEAM_COLORS = {
    "KC": "#E31837",
    "BUF": "#00338D",
    "PHI": "#004C54",
    "SF": "#AA0000",
    "DAL": "#003594",
    "GB": "#203731",
    "CHI": "#0B162A",
    "BAL": "#241773",
    # Add more as needed
}

def team_color(team):
    return TEAM_COLORS.get(team, "#00E0FF")
# -----------------------------
# METRIC CARDS
# -----------------------------

def metric_row(metrics):
    """
    Display a row of metric cards.
    metrics = [
        ("EPA/play", "+0.12"),
        ("Success Rate", "48%"),
        ("Win Prob", "67%")
    ]
    """
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)


# -----------------------------
# CHARTS
# -----------------------------

def line_chart(df, x, y, title=None, tooltip=None, color="#00E0FF"):
    """Reusable NDH‑style line chart."""
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X(x, title=x.replace("_", " ").title()),
            y=alt.Y(y, title=y.replace("_", " ").title()),
            color=alt.value(color),
            tooltip=tooltip or [x, y],
        )
        .properties(height=350, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def scatter_chart(df, x, y, color_field="team", title=None, tooltip=None):
    """EPA vs Yards, EPA vs Dropbacks, etc."""
    chart = (
        alt.Chart(df)
        .mark_circle(size=80)
        .encode(
            x=alt.X(x, title=x.replace("_", " ").title()),
            y=alt.Y(y, title=y.replace("_", " ").title()),
            color=color_field,
            tooltip=tooltip or [x, y, color_field],
        )
        .properties(height=400, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def win_prob_chart(df):
    """Win probability line chart."""
    chart = (
        alt.Chart(df)
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


