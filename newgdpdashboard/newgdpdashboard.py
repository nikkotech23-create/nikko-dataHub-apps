import io
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import pycountry
import pycountry_convert as pc

# --------------------------------------------------
# Helpers: ISO + continent + region mapping
# --------------------------------------------------

def iso3_to_iso2(iso3):
    try:
        return pycountry.countries.get(alpha_3=iso3).alpha_2
    except:
        return None

def iso2_to_continent(iso2):
    try:
        code = pc.country_alpha2_to_continent_code(iso2)
        return pc.convert_continent_code_to_continent_name(code)
    except:
        return None

def refine_region(continent, country):
    """Split Americas into North America vs Latin America & Caribbean."""
    north_america = {
        "United States", "Canada", "Mexico", "Greenland", "Bermuda"
    }

    if continent == "North America":
        if country in north_america:
            return "North America"
        else:
            return "Latin America & Caribbean"

    return continent

# --------------------------------------------------
# World Bank fetch
# --------------------------------------------------
def fetch_indicator(indicator_code):
    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
        "?format=json&per_page=20000"
    )
    r = requests.get(url).json()

    # Some API responses return only 1 element (error)
    if len(r) < 2:
        return pd.DataFrame(columns=["country", "iso3", "year", indicator_code])

    data = r[1]

    rows = []
    for item in data:
        # country can be dict or string
        country_name = (
            item["country"]["value"]
            if isinstance(item["country"], dict)
            else item["country"]
        )

        iso3 = item.get("countryiso3code", None)
        year = item.get("date", None)
        value = item.get("value", None)

        # Skip rows with missing year
        if year is None:
            continue

        rows.append([country_name, iso3, int(year), value])

    df = pd.DataFrame(rows, columns=["country", "iso3", "year", indicator_code])
    return df


@st.cache_data(show_spinner=True)
def load_worldbank_data():
    # GDP (current US$)
    gdp = fetch_indicator("NY.GDP.MKTP.CD")
    # Population
    pop = fetch_indicator("SP.POP.TOTL")
    # GDP per capita (current US$)
    gdp_pc = fetch_indicator("NY.GDP.PCAP.CD")

    # Merge
    df = gdp.merge(pop, on=["country", "iso3", "year"], how="outer")
    df = df.merge(gdp_pc, on=["country", "iso3", "year"], how="outer")

    # Rename for clarity
    df = df.rename(
        columns={
            "NY.GDP.MKTP.CD": "gdp",
            "SP.POP.TOTL": "population",
            "NY.GDP.PCAP.CD": "gdp_per_capita",
        }
    )

    # ISO2 + continent + region
    df["iso2"] = df["iso3"].apply(iso3_to_iso2)
    df["continent"] = df["iso2"].apply(iso2_to_continent)
    df["region_group"] = df.apply(
        lambda row: refine_region(row["continent"], row["country"]),
        axis=1,
    )

    # Drop rows without region or GDP
    df = df.dropna(subset=["region_group", "gdp"])

    # GDP growth (YoY %)
    df = df.sort_values(["country", "year"])
    df["gdp_growth_pct"] = (
        df.groupby("country")["gdp"].pct_change() * 100
    )

    return df

df = load_worldbank_data()

regions = [
    "Europe",
    "North America",
    "Latin America & Caribbean",
    "Asia",
    "Oceania",
    "Africa",
]

# --------------------------------------------------
# Page config (theme hooks)
# --------------------------------------------------

st.set_page_config(
    page_title="Global GDP Dashboard",
    layout="wide",
)

st.title("🌍 Global GDP Dashboard (World Bank Data)")
st.caption("GDP, population, GDP per capita, and growth — with regional and multi‑region views.")

# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab_single, tab_compare = st.tabs(["Single region dashboard", "Multi‑region comparison"])

# ==================================================
# TAB 1: Single region dashboard
# ==================================================
with tab_single:
    st.sidebar.header("Single region filters")

    selected_region = st.sidebar.selectbox("Region", regions)
    years = sorted(df["year"].unique())
    selected_year = st.sidebar.slider(
        "Year", min(years), max(years), max(years)
    )

    # Country search bar (within region)
    region_df_all_years = df[df["region_group"] == selected_region]
    all_region_countries = sorted(region_df_all_years["country"].unique())
    search_query = st.sidebar.text_input("Search country (optional)")
    if search_query:
        filtered_countries = [
            c for c in all_region_countries
            if search_query.lower() in c.lower()
        ]
    else:
        filtered_countries = all_region_countries

    selected_country = st.sidebar.selectbox(
        "Country (time series)", filtered_countries
    )

    # Filter for year + region
    df_year_region = df[
        (df["region_group"] == selected_region)
        & (df["year"] == selected_year)
    ]

    st.subheader(f"{selected_region} — {selected_year}")

    if df_year_region.empty:
        st.warning("No data available for this selection.")
    else:
        # KPIs
        total_gdp = df_year_region["gdp"].sum()
        total_pop = df_year_region["population"].sum()
        avg_gdp_pc = df_year_region["gdp_per_capita"].mean()
        avg_growth = df_year_region["gdp_growth_pct"].mean()

        top_row = df_year_region.sort_values("gdp", ascending=False).iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total GDP (US$)", f"{total_gdp:,.0f}")
        col2.metric("Total population", f"{total_pop:,.0f}")
        col3.metric("Avg GDP per capita (US$)", f"{avg_gdp_pc:,.0f}")
        col4.metric("Avg GDP growth (%)", f"{avg_growth:,.2f}")

        # Map + bar
        col_map, col_bar = st.columns([2, 1])

        with col_map:
            st.markdown("### GDP map")
            fig_map = px.choropleth(
                df_year_region,
                locations="iso3",
                color="gdp",
                hover_name="country",
                hover_data={
                    "gdp": ":,.0f",
                    "population": ":,.0f",
                    "gdp_per_capita": ":,.0f",
                    "gdp_growth_pct": ":,.2f",
                },
                color_continuous_scale="Viridis",
                title=f"GDP by country — {selected_region} ({selected_year})",
            )
            st.plotly_chart(fig_map, use_container_width=True)

        with col_bar:
            st.markdown("### GDP ranking")
            df_bar = df_year_region.sort_values("gdp", ascending=False)
            fig_bar = px.bar(
                df_bar,
                x="gdp",
                y="country",
                orientation="h",
                hover_data=["population", "gdp_per_capita", "gdp_growth_pct"],
            )
            fig_bar.update_layout(
                yaxis={"categoryorder": "total ascending"},
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Time series for selected country
        st.markdown(f"### Time series — {selected_country}")
        df_country = df[df["country"] == selected_country].sort_values("year")

        ts_metric = st.selectbox(
            "Metric",
            ["gdp", "population", "gdp_per_capita", "gdp_growth_pct"],
            format_func=lambda x: {
                "gdp": "GDP (US$)",
                "population": "Population",
                "gdp_per_capita": "GDP per capita (US$)",
                "gdp_growth_pct": "GDP growth (%)",
            }[x],
        )

        fig_ts = px.line(
            df_country,
            x="year",
            y=ts_metric,
            markers=True,
            title=f"{ts_metric} over time — {selected_country}",
        )
        st.plotly_chart(fig_ts, use_container_width=True)

        # Download buttons (CSV + Excel) for current region/year
        st.markdown("### Download data (current region & year)")
        csv_data = df_year_region.to_csv(index=False).encode("utf-8")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_year_region.to_excel(writer, index=False, sheet_name="data")
        excel_data = buffer.getvalue()

        col_dl1, col_dl2 = st.columns(2)
        col_dl1.download_button(
            "Download CSV",
            data=csv_data,
            file_name=f"gdp_{selected_region}_{selected_year}.csv",
            mime="text/csv",
        )
        col_dl2.download_button(
            "Download Excel",
            data=excel_data,
            file_name=f"gdp_{selected_region}_{selected_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# ==================================================
# TAB 2: Multi‑region comparison
# ==================================================
with tab_compare:
    st.sidebar.header("Comparison filters")

    compare_regions = st.sidebar.multiselect(
        "Regions to compare",
        regions,
        default=["Europe", "Asia"],
    )

    years = sorted(df["year"].unique())
    compare_year = st.sidebar.slider(
        "Year (comparison)", min(years), max(years), max(years)
    )

    df_compare = df[
        (df["region_group"].isin(compare_regions))
        & (df["year"] == compare_year)
    ]

    st.subheader(f"Multi‑region comparison — {compare_year}")

    if df_compare.empty or len(compare_regions) == 0:
        st.info("Select at least one region with available data.")
    else:
        # Aggregate by region
        agg = (
            df_compare.groupby("region_group")
            .agg(
                total_gdp=("gdp", "sum"),
                total_population=("population", "sum"),
                avg_gdp_per_capita=("gdp_per_capita", "mean"),
                avg_gdp_growth=("gdp_growth_pct", "mean"),
            )
            .reset_index()
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### Total GDP by region")
            fig_gdp = px.bar(
                agg,
                x="region_group",
                y="total_gdp",
                labels={"total_gdp": "Total GDP (US$)", "region_group": "Region"},
            )
            st.plotly_chart(fig_gdp, use_container_width=True)

        with col_b:
            st.markdown("### Total population by region")
            fig_pop = px.bar(
                agg,
                x="region_group",
                y="total_population",
                labels={"total_population": "Population", "region_group": "Region"},
            )
            st.plotly_chart(fig_pop, use_container_width=True)

        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("### Avg GDP per capita by region")
            fig_pc = px.bar(
                agg,
                x="region_group",
                y="avg_gdp_per_capita",
                labels={
                    "avg_gdp_per_capita": "Avg GDP per capita (US$)",
                    "region_group": "Region",
                },
            )
            st.plotly_chart(fig_pc, use_container_width=True)

        with col_d:
            st.markdown("### Avg GDP growth (%) by region")
            fig_gr = px.bar(
                agg,
                x="region_group",
                y="avg_gdp_growth",
                labels={
                    "avg_gdp_growth": "Avg GDP growth (%)",
                    "region_group": "Region",
                },
            )
            st.plotly_chart(fig_gr, use_container_width=True)

        # Download aggregated comparison
        st.markdown("### Download comparison data")
        csv_comp = agg.to_csv(index=False).encode("utf-8")
        buffer_comp = io.BytesIO()
        with pd.ExcelWriter(buffer_comp, engine="xlsxwriter") as writer:
            agg.to_excel(writer, index=False, sheet_name="comparison")
        excel_comp = buffer_comp.getvalue()

        col_dl3, col_dl4 = st.columns(2)
        col_dl3.download_button(
            "Download comparison CSV",
            data=csv_comp,
            file_name=f"gdp_comparison_{compare_year}.csv",
            mime="text/csv",
        )
        col_dl4.download_button(
            "Download comparison Excel",
            data=excel_comp,
            file_name=f"gdp_comparison_{compare_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        )
