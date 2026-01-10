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
# Database Engine (cached resource)
# -----------------------------
@st.cache_resource
def get_engine():
    """
    Create and cache the SQLAlchemy engine.
    """
    try:
        engine = create_engine(st.secrets["DB_URL"], connect_args={"sslmode": "require"})
        return engine
    except Exception as e:
        st.error("Failed to create database engine.")
        st.text(f"Error details: {e}")
        return None

engine = get_engine()

# -----------------------------
# Load Data Function with Retry Logic (cached)
# -----------------------------
@st.cache_data
def load_data(max_retries=3, delay=2):
    """
    Load data from PostgreSQL with automatic retries.

    Args:
        max_retries (int): Number of retry attempts if connection fails.
        delay (int or float): Initial delay (in seconds) between retries, doubles each retry.

    Returns:
        pd.DataFrame: Query result or empty DataFrame if all retries fail.
    """
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
            st.text(f"Error details: {e}")
            time.sleep(delay)
            delay *= 2  # exponential backoff
        except Exception as e:
            st.error("An unexpected error occurred while loading data.")
            st.text(f"Error details: {e}")
            return pd.DataFrame()

    st.error(f"Failed to load data after {max_retries} attempts. Please check your database.")
    return pd.DataFrame()

# -----------------------------
# Fetch Data with Spinner
# -----------------------------
with st.spinner("Loading data from database..."):
    df = load_data(max_retries=5, delay=2)

if df.empty:
    st.warning("No data available. Check your database or query.")
else:
    # -----------------------------
    # Show Raw Data
    # -----------------------------
    st.subheader("Raw OLA Ride Data")
    st.dataframe(df)

    # -----------------------------
    # Vehicle Type Analysis
    # -----------------------------
    st.subheader("Rides by Vehicle Type")
    if "vehicle_type" in df.columns:
        vehicle_counts = df["vehicle_type"].value_counts()
        st.bar_chart(vehicle_counts)
    else:
        st.warning("Column 'vehicle_type' not found in database table.")

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
        st.warning("Column 'booking_status' not found in database table.")







