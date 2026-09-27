"""
dashboard.py
Day 23/24: Substation Live Monitoring Dashboard
IED-1/IED-2 status, event log table, aur fault current graph dikhata hai.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Substation Live Monitoring", layout="wide")

st.title("Substation Live Monitoring Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("IED-1 (Relay)")
    st.metric(label="Status", value="Normal")

with col2:
    st.subheader("IED-2 (Breaker)")
    st.metric(label="Status", value="Tripped")

st.subheader("Event Log")
log_df = pd.read_csv("event_log.csv")
st.dataframe(log_df, use_container_width=True)

st.subheader("Fault Current Over Time (kA)")
st.line_chart(log_df.set_index("time")["fault_current_ka"])
