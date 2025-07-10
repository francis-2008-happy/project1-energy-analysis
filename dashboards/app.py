import streamlit as st
import pandas as pd
import plotly.express as px  # type: ignore
from typing import List
import numpy as np
import plotly.graph_objects as go


# Load cleaned dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/merged_data.csv", parse_dates=["date"])


df = load_data()

# Sidebar filters
st.sidebar.title("Filters")
date_range = st.sidebar.date_input("Date Range", [df.date.min(), df.date.max()])
cities: List[str] = st.sidebar.multiselect(
    "Select Cities", df["city"].unique(), default=list(df["city"].unique())
)

# Handle date unpacking safely
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.error("Please select a start and end date.")
    st.stop()

# Filter data
filtered_df = df[
    (df["date"] >= pd.to_datetime(start_date))
    & (df["date"] <= pd.to_datetime(end_date))
]
filtered_df = filtered_df[filtered_df["city"].isin(cities)]

# App title
st.title("🔌 US Weather + Energy Dashboard")
st.caption(f"Last data update: {df['date'].max().date()}")

# Geographic overview / Navigation

st.header("1️⃣ Geographic Overview")
st.subheader("Temperature + Energy Use by City")

# Show table for now
st.dataframe(
    filtered_df.groupby("city")
    .agg({"temp_max": "last", "energy_usage_mwh": "last"})
    .rename(
        columns={
            "temp_max": "Latest Max Temp (°F)",
            "energy_usage_mwh": "Latest Energy (MWh)",
        }
    )
    .reset_index()
)


# Coordinates for the 5 cities
city_coords = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Seattle": {"lat": 47.6062, "lon": -122.3321}
}

# latest date in the dataset
latest_date = filtered_df["date"].max()
yesterday_date = latest_date - pd.Timedelta(days=1)

# Calculate latest and yesterday’s values
latest = filtered_df[filtered_df["date"] == latest_date].copy()
yesterday = filtered_df[filtered_df["date"] == yesterday_date].copy()

# Merge to compare % change
merged = pd.merge(
    latest[["city", "temp_max", "energy_usage_mwh"]],
    yesterday[["city", "energy_usage_mwh"]],
    on="city",
    suffixes=("", "_yesterday")
)

# Compute percent change
merged["percent_change"] = ((merged["energy_usage_mwh"] - merged["energy_usage_mwh_yesterday"]) / 
                            merged["energy_usage_mwh_yesterday"]) * 100

# Add lat/lon
merged["lat"] = merged["city"].apply(lambda x: city_coords[x]["lat"])
merged["lon"] = merged["city"].apply(lambda x: city_coords[x]["lon"])

# Color code by energy usage
def usage_color(pct):
    if pct > 5:
        return "red"
    elif pct < -5:
        return "green"
    else:
        return "orange"

merged["color"] = merged["percent_change"].apply(usage_color)

# Plot with Plotly

# fig = px.scatter_map(
#     merged,
#     lat="lat",
#     lon="lon",
#     color="color",
#     size="energy_usage_mwh",
#     size_max=30,
#     zoom=3,
#     hover_name="city",
#     mapbox_style="open-street-map",
# )

fig = px.scatter_mapbox(
    merged,
    lat="lat",
    lon="lon",
    color="color",
    size="energy_usage_mwh",
    size_max=30,
    zoom=3,
    hover_name="city",
    hover_data={
        "temp_max": True,
        "energy_usage_mwh": True,
        "percent_change": True,  # <-- This is okay now that it's only here
        "lat": False,
        "lon": False,
        "color": False,
    },
    mapbox_style="open-street-map",
)

# Add to Streamlit
st.plotly_chart(fig, use_container_width=True)




# 2 Time Series Analysis

st.header("2️⃣ Time Series Analysis")
st.subheader("Temperature vs Energy Usage Over Time")

# Dropdown to select city
city_option = st.selectbox("Select City", ["All Cities"] + list(df["city"].unique()))

# Filter based on selection
if city_option != "All Cities":
    city_df = filtered_df[filtered_df["city"] == city_option]
else:
    city_df = filtered_df.copy()

# Create figure
fig = go.Figure()

# Temperature line (left y-axis)
fig.add_trace(
    go.Scatter(
        x=city_df["date"],
        y=city_df["temp_max"],
        mode="lines",
        name="Max Temp (°F)",
        line=dict(color="firebrick", width=2),
        yaxis="y1",
    )
)

# Energy usage line (right y-axis)
fig.add_trace(
    go.Scatter(
        x=city_df["date"],
        y=city_df["energy_usage_mwh"],
        mode="lines",
        name="Energy (MWh)",
        line=dict(color="royalblue", width=2, dash="dash"),
        yaxis="y2",
    )
)

# Weekend shading
for date in pd.date_range(city_df["date"].min(), city_df["date"].max()):
    if date.weekday() >= 5:  # Saturday or Sunday
        fig.add_vrect(
            x0=date,
            x1=date + pd.Timedelta(days=1),
            fillcolor="LightGray",
            opacity=0.3,
            layer="below",
            line_width=0,
        )

# Layout configuration
fig.update_layout(
    title=f"Temperature vs Energy Usage - {city_option}",
    xaxis_title="Date",
    yaxis=dict(title="Max Temp (°F)", side="left"),
    yaxis2=dict(title="Energy Usage (MWh)", overlaying="y", side="right"),
    legend=dict(x=0.01, y=1.15, orientation="h"),
    height=700,
)

st.plotly_chart(fig, use_container_width=True)




# 3 Correlation Analysis

st.header("3️⃣ Correlation Analysis")
st.subheader("Temperature vs Energy Usage")

# Filter only rows with valid data
corr_df = filtered_df.dropna(subset=["temp_max", "energy_usage_mwh"])

# Compute correlation
correlation = corr_df["temp_max"].corr(corr_df["energy_usage_mwh"])
r_squared = round(correlation**2, 3)

# Show values
st.markdown(f"**Correlation coefficient (r):** {round(correlation, 3)}")
st.markdown(f"**R² value:** {r_squared}")

# Plotly scatter plot
fig = px.scatter(
    corr_df,
    x="temp_max",
    y="energy_usage_mwh",
    color="city",
    hover_data=["date", "city"],
    labels={"temp_max": "Max Temp (°F)", "energy_usage_mwh": "Energy Usage (MWh)"},
    title="Correlation between Temperature and Energy Usage",
)

# Add regression line using Plotly trendline
fig = px.scatter(
    corr_df,
    x="temp_max",
    y="energy_usage_mwh",
    color="city",
    trendline="ols",
    trendline_color_override="black",
    hover_data=["date"],
    labels={"temp_max": "Max Temp (°F)", "energy_usage_mwh": "Energy Usage (MWh)"},
)

# Add R-squared as annotation
fig.add_annotation(
    xref="paper",
    yref="paper",
    x=0.05,
    y=0.95,
    text=f"R² = {r_squared}",
    showarrow=False,
    font=dict(size=14, color="black"),
    bordercolor="black",
    borderwidth=1,
    bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)




# 4 Visualization 4 – Usage Patterns Heatmap
st.header("4️⃣ Usage Patterns Heatmap")
st.subheader("Average Energy Usage by Temperature and Day of Week")

# Define temperature bins
temp_bins = [-float("inf"), 50, 60, 70, 80, 90, float("inf")]
temp_labels = ["<50°F", "50-60°F", "60-70°F", "70-80°F", "80-90°F", ">90°F"]

# Bin the max temperature
filtered_df["temp_range"] = pd.cut(filtered_df["temp_max"], bins=temp_bins, labels=temp_labels)

# Add a day-of-week column
filtered_df["day_of_week"] = filtered_df["date"].dt.day_name()

# Group by day and temperature range to get average energy usage
heatmap_data = filtered_df.groupby(["temp_range", "day_of_week"])["energy_usage_mwh"].mean().reset_index()

# Pivot to matrix format for heatmap
heatmap_matrix = heatmap_data.pivot(index="temp_range", columns="day_of_week", values="energy_usage_mwh")

# Reorder the days
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_matrix = heatmap_matrix[day_order]

# Plot heatmap using Plotly
fig = px.imshow(
    heatmap_matrix,
    labels=dict(x="Day of Week", y="Temperature Range", color="Avg Energy (MWh)"),
    color_continuous_scale="RdBu_r",
    text_auto=".2f",
    height=600
)

# Show heatmap
st.plotly_chart(fig, use_container_width=True)
