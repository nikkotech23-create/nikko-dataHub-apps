import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# -----------------------------
# Load World Bank Indicator
# -----------------------------
def load_worldbank_indicator(indicator):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=20000"
    r = requests.get(url).json()
    rows = r[1]

    data = []
    for row in rows:
        if row["value"] is not None:
            data.append({
                "country": row["country"]["value"],
                "iso3": row["countryiso3code"],
                "year": int(row["date"]),
                "value": row["value"]
            })
    return pd.DataFrame(data)

# -----------------------------
# Load GDP + Population
# -----------------------------
@st.cache_data
def load_data():
    gdp = load_worldbank_indicator("NY.GDP.MKTP.CD")       # GDP (current US$)
    pop = load_worldbank_indicator("SP.POP.TOTL")          # Population

    df = pd.merge(gdp, pop, on=["country", "iso3", "year"], suffixes=("_gdp", "_pop"))
    df["gdp_per_capita"] = df["value_gdp"] / df["value_pop"]
    return df

df = load_data()

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="World Bank Global Dashboard", layout="wide")

st.title("🌍 World Bank Global Dashboard")
st.markdown("Explore GDP, Population, and GDP per Capita using real-time World Bank data.")

# Sidebar
st.sidebar.header("Controls")

# Light/Dark mode toggle
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
template = "plotly_dark" if theme == "Dark" else "plotly_white"

# Year selector (extend to 2026)
years = sorted(df["year"].unique(), reverse=True)
years = [y for y in years if y <= 2026]  # ensure max year is 2026
year = st.sidebar.selectbox("Select Year", years)

# Metric selector
metric = st.sidebar.selectbox(
    "Metric",
    ["GDP (current US$)", "Population", "GDP per Capita"]
)

# Filter by year
df_year = df[df["year"] == year].copy()

# Choose metric
if metric == "GDP (current US$)":
    df_year["metric"] = df_year["value_gdp"]
    color_scale = "Viridis"
elif metric == "Population":
    df_year["metric"] = df_year["value_pop"]
    color_scale = "Plasma"
else:
    df_year["metric"] = df_year["gdp_per_capita"]
    color_scale = "Cividis"

# -----------------------------
# World Map
# -----------------------------
st.subheader(f"🌐 {metric} in {year}")

fig_map = px.choropleth(
    df_year,
    locations="iso3",
    color="metric",
    hover_name="country",
    color_continuous_scale=color_scale,
    projection="natural earth",
    template=template
)

fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# World Totals
# -----------------------------
st.subheader("🌎 Global Totals")

colA, colB, colC = st.columns(3)

colA.metric("Total World GDP", f"${df_year['value_gdp'].sum():,.0f}")
colB.metric("Total World Population", f"{df_year['value_pop'].sum():,}")
colC.metric("Average GDP per Capita", f"${df_year['gdp_per_capita'].mean():,.0f}")

# -----------------------------
# Country-Level Charts
# -----------------------------
st.subheader(f"📊 Country-Level Analysis ({metric})")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top 10 Countries")
    top10 = df_year.sort_values("metric", ascending=False).head(10)
    fig_top10 = px.bar(
        top10,
        x="country",
        y="metric",
        text_auto=".2s",
        template=template
    )
    fig_top10.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_top10, use_container_width=True)

with col2:
    st.markdown("### Bottom 10 Countries")
    bottom10 = df_year.sort_values("metric", ascending=True).head(10)
    fig_bottom10 = px.bar(
        bottom10,
        x="country",
        y="metric",
        text_auto=".2s",
        template=template
    )
    fig_bottom10.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bottom10, use_container_width=True)

# -----------------------------
# Data Table
# -----------------------------
st.subheader("📄 Full Data Table")
st.dataframe(
    df_year[["country", "value_gdp", "value_pop", "gdp_per_capita"]]
    .sort_values("value_gdp", ascending=False),
    use_container_width=True
)
