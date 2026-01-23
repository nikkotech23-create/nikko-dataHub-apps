# core/data_loader.py

import nfl_data_py as nfl
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_pbp(seasons):
    """Load play-by-play data for given seasons."""
    df = nfl.import_pbp_data(
        years=seasons,
        downcast=True
    )
    return df
@st.cache_data(show_spinner=False)
def load_weekly(seasons):
    """Load weekly team/player stats."""
    df = nfl.import_weekly_data(
        years=seasons,
        downcast=True
    )
    return df

@st.cache_data(show_spinner=False)
def load_rosters(seasons):
    """Load roster data."""
    df = nfl.import_rosters(
        years=seasons
    )
    return df

@st.cache_data(show_spinner=False)
def load_schedules(seasons):
    """Load schedules for given seasons."""
    df = nfl.import_schedules(
        years=seasons
    )
    return df

@st.cache_data(show_spinner=False)
def load_teams():
    """Load static team metadata."""
    df = nfl.import_team_desc()
    return df

  
