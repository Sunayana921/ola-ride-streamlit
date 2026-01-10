import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="OLA Ride Analytics", layout="wide")
st.title("OLA Ride Analysis Dashboard")
st.write("PostgreSQL + Streamlit integration successful!")

# -----------------------------
# Database Engine (cached)
# -----------------------------
@st.cache_resource
def get_engine():
    try:
        engine = create_engine(st.secrets["DB_URL"], connect_args={"sslmode": "require"})
        return engine
    except Exception as e:
        st.error("Failed to create database engine.")
        st.text(str(e))
        return None

engine = get_engine()
st.write(pd.read_sql("SELECT current_database()", engine))
# -----------------------------
# Load Data with Retry Logic
# -----------------------------
@st.cache_data
def load_data(max_retries=3, delay=2):
    if engine is None:
        return pd.DataFrame()

    query = "SELECT * FROM ola.olaride"
    attempt = 0
    while attempt < max_retries:
        try:
            df = pd.read_sql(query, engine)
            return df
        except OperationalError as e:
            attempt += 1
            st.warning(f"Database connection failed (attempt {attempt}/{max_retries}). Retrying in {delay} seconds...")
            st.text(str(e))
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            st.error("Unexpected error while loading data.")
            st.text(str(e))
            return pd.DataFrame()

    st.error(f"Failed to load data after {max_retries} attempts. Check DB host, username, and password.")
    return pd.DataFrame()

# -----------------------------
# Fetch Data
# -----------------------------
with st.spinner("Loading data from database..."):
    df = load_data(max_retries=5, delay=2)

if df.empty:
    st.warning("No data available. Check your database or query.")
else:
    # -----------------------------
    # Raw Data
    # -----------------------------
    st.subheader("Raw OLA Ride Data")
    st.dataframe(df)

    # -----------------------------
    # Vehicle Type Analysis
    # -----------------------------
    st.subheader("Rides by Vehicle Type")
    if "vehicle_type" in df.columns:
        st.bar_chart(df["vehicle_type"].value_counts())
    else:
        st.warning("Column 'vehicle_type' not found.")

    # -----------------------------
    # Sidebar Filters
    # -----------------------------
    st.sidebar.header("Filters")
    if "vehicle_type" in df.columns:
        vehicle_filter = st.sidebar.multiselect(
            "Select Vehicle Type",
            options=df["vehicle_type"].unique(),
            default=df["vehicle_type"].unique()
        )
        filtered_df = df[df["vehicle_type"].isin(vehicle_filter)]
    else:
        filtered_df = df

    # -----------------------------
    # Filtered Data Table
    # -----------------------------
    st.subheader("Filtered Data")
    st.dataframe(filtered_df)

    # -----------------------------
    # Metrics
    # -----------------------------
    if "booking_status" in filtered_df.columns:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rides", len(filtered_df))
        col2.metric("Completed Rides", len(filtered_df[filtered_df["booking_status"] == "Completed"]))
        col3.metric("Cancelled Rides", len(filtered_df[filtered_df["booking_status"] != "Completed"]))
    else:
        st.warning("Column 'booking_status' not found.")









