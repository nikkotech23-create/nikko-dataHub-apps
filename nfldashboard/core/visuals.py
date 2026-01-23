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

def filter_bar(options):
    """
    options = {
        "Season": [2024, 2023, 2022],
        "Team": ["KC", "BUF", "PHI"],
        "Position": ["QB", "RB", "WR"]
    }
    Returns a dict of selected values.
    """
    cols = st.columns(len(options))
    selections = {}

    for col, (label, values) in zip(cols, options.items()):
        selections[label] = col.selectbox(label, values)

    return selections

 def epa_heatmap(df, x, y, value="epa", title="EPA Heatmap"):
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X(x + ":O", title=x.replace("_", " ").title()),
            y=alt.Y(y + ":O", title=y.replace("_", " ").title()),
            color=alt.Color(value + ":Q", scale=alt.Scale(scheme="turbo")),
            tooltip=[x, y, value],
        )
        .properties(height=400, title=title)
    )
    st.altair_chart(chart, use_container_width=True)

 def route_tree(df, title="Route Tree"):
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("x:Q", title="Field Width"),
            y=alt.Y("y:Q", title="Field Length"),
            color="route:N",
            tooltip=["route", "x", "y"],
        )
        .properties(height=500, title=title)
    )
    st.altair_chart(chart, use_container_width=True)

def pressure_map(df, title="Pressure Heatmap"):
    chart = (
        alt.Chart(df)
        .mark_circle(opacity=0.6)
        .encode(
            x="x:Q",
            y="y:Q",
            size="pressure:Q",
            color=alt.Color("pressure:Q", scale=alt.Scale(scheme="inferno")),
            tooltip=["x", "y", "pressure"],
        )
        .properties(height=500, title=title)
    )
    st.altair_chart(chart, use_container_width=True)

def drive_chart(df, title="Drive Chart"):
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("play_index:Q", title="Play Number"),
            y=alt.Y("yardline_100:Q", title="Distance to End Zone"),
            color="drive:N",
            tooltip=["drive", "posteam", "yardline_100", "desc"],
        )
        .properties(height=400, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


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


