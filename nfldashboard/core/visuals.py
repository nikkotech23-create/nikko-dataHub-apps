# core/visuals.py

import streamlit as st
import altair as alt
import pandas as pd

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


