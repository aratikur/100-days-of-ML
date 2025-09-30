# shark_live_tracker.py
import pandas as pd
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# ----------------------------
# Load Shark Data
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("global_shark_activity_100k.csv")
    return df

df = load_data()

st.title("🌊 Global Shark Live Tracker")
st.markdown("Track shark sightings, temperature, chlorophyll, and hotspots around the globe!")

# ----------------------------
# Sidebar Filters
# ----------------------------
regions = df["Region"].unique().tolist()
selected_region = st.sidebar.multiselect("Select Region(s):", regions, default=regions)
min_sightings = st.sidebar.slider("Minimum Shark Sightings:", 0, int(df["Shark_Sightings"].max()), 0)

filtered_df = df[(df["Region"].isin(selected_region)) & (df["Shark_Sightings"] >= min_sightings)]

st.markdown(f"Showing {len(filtered_df)} records based on your filters.")

# ----------------------------
# Scatter Plots
# ----------------------------
st.subheader("Shark Sightings vs Sea Surface Temperature (°C)")
st.bar_chart(filtered_df.groupby("Sea_Surface_Temperature_C")["Shark_Sightings"].sum())

st.subheader("Shark Sightings vs Chlorophyll (mg/m³)")
st.bar_chart(filtered_df.groupby("Chlorophyll_mg_m3")["Shark_Sightings"].sum())

# ----------------------------
# Interactive Map
# ----------------------------
st.subheader("Global Shark Hotspots")

# Center map roughly at global center
m = folium.Map(location=[0, 0], zoom_start=2)

# Add Circle markers
for idx, row in filtered_df.iterrows():
    folium.Circle(
        location=[row["Latitude"], row["Longitude"]],
        radius=row["Shark_Sightings"]*5000,  # scale radius by sightings
        color="red",
        fill=True,
        fill_opacity=0.5,
        popup=f"Region: {row['Region']}<br>Sightings: {row['Shark_Sightings']}<br>SST: {row['Sea_Surface_Temperature_C']} °C<br>Chlorophyll: {row['Chlorophyll_mg_m3']} mg/m³"
    ).add_to(m)

# Optionally, add HeatMap
heat_data = [[row["Latitude"], row["Longitude"], row["Shark_Sightings"]] for idx, row in filtered_df.iterrows()]
HeatMap(heat_data, radius=25).add_to(m)

# Display map in Streamlit
st_data = st_folium(m, width=1200, height=600)

# ----------------------------
# Data Table
# ----------------------------
st.subheader("Data Table")
st.dataframe(filtered_df)
