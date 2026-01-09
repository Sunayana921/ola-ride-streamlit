import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.title("Hello Streamlit 🚀")
import streamlit as st

st.set_page_config(page_title="OLA Ride Analytics", layout="wide")

st.title("🚕 OLA Ride Analysis Dashboard")
st.write("PostgreSQL + Streamlit integration successful!")
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

engine = create_engine(
    "postgresql+psycopg2://ola_user:ola2029!@localhost:5432/ola_anallysis"
)
@st.cache_data
def load_data():
    query = "SELECT * FROM ola.olaride"
    return pd.read_sql(query, engine)

df = load_data()

st.subheader("Raw OLA Ride Data")
st.dataframe(df)
st.subheader("Rides by Vehicle Type")

vehicle_counts = df["vehicle_type"].value_counts()

st.bar_chart(vehicle_counts)
st.sidebar.header("Filters")

vehicle_filter = st.sidebar.multiselect(
    "Select Vehicle Type",
    options=df["vehicle_type"].unique(),
    default=df["vehicle_type"].unique()
)

filtered_df = df[df["vehicle_type"].isin(vehicle_filter)]

st.subheader("Filtered Data")
st.dataframe(filtered_df)
col1, col2, col3 = st.columns(3)

col1.metric("Total Rides", len(filtered_df))
col2.metric("Completed Rides", len(filtered_df[filtered_df["booking_status"] == "Completed"]))
col3.metric("Cancelled Rides", len(filtered_df[filtered_df["booking_status"] != "Completed"]))

