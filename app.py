import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="OLA Ride Analytics", layout="wide")

st.title("OLA Ride Analysis Dashboard")
st.write("PostgreSQL + Streamlit integration successful!")

# -----------------------------
# Database Connection (Neon Cloud)
# -----------------------------
# Make sure you add your Neon URL in Streamlit Secrets as:
# DB_URL = "postgresql://neondb_owner:password@ep-xyz.neon.tech/ola_analysis?sslmode=require"

engine = create_engine(st.secrets["DB_URL"], connect_args={"sslmode": "require"})

# -----------------------------
# Load Data Function
# -----------------------------
@st.cache_data
def load_data():
    query = "SELECT * FROM ola.olaride"
    return pd.read_sql(query, engine)

df = load_data()

# -----------------------------
# Show Raw Data
# -----------------------------
st.subheader("Raw OLA Ride Data")
st.dataframe(df)

# -----------------------------
# Vehicle Type Analysis
# -----------------------------
st.subheader("Rides by Vehicle Type")
vehicle_counts = df["vehicle_type"].value_counts()
st.bar_chart(vehicle_counts)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

vehicle_filter = st.sidebar.multiselect(
    "Select Vehicle Type",
    options=df["vehicle_type"].unique(),
    default=df["vehicle_type"].unique()
)

filtered_df = df[df["vehicle_type"].isin(vehicle_filter)]

# -----------------------------
# Filtered Data Table
# -----------------------------
st.subheader("Filtered Data")
st.dataframe(filtered_df)

# -----------------------------
# Metrics
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Rides", len(filtered_df))
col2.metric("Completed Rides", len(filtered_df[filtered_df["booking_status"] == "Completed"]))
col3.metric("Cancelled Rides", len(filtered_df[filtered_df["booking_status"] != "Completed"]))




