import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import sys
import os
import threading, time
import random
import altair as alt
from pages.alerts import flag_hot_sku, alert_severity_map # 2nd import is temporary
from components.DOS_bar_chart import fetch_DOS_count
from db import get_all_data, WarehouseData

def main():
    """
    Launches a real-time Streamlit dashboard for monitoring dock status and SKU alerts.

    This function:
    - Retrieves warehouse data using `get_all_data()`.
    - Configures the Streamlit page layout and title.
    - Continuously updates the dashboard every 2 seconds by:
        - Randomizing the 'Days of Service' value for a random SKU.
        - Updating the 'Last Refresh' timestamp.
        - Applying conditional formatting to highlight SKUs based on service days.
    - Displays multiple dataframes including alerts, SKUs, dock status, production pipeline, and all SKUs.

    Note:
        This function runs an infinite loop to simulate real-time updates.
        To stop the dashboard, interrupt the Streamlit app manually.
    """
    data = get_all_data()
    st.set_page_config(
        page_title="Real-time Dock Status Dashboard",
        page_icon="📦",
        layout="wide",
    )
    
    st.title("Dock Status Dashboard")  
    placeholder = st.empty()
   
    # Real-time data simulation loop
    while True:
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            # Randomize 'Days of Service' for a random SKU
            random_row = data.dock_status.sample(n=1)
            random_index = random_row.index[0]
            data.dock_status.loc[random_index, 'Days of Service'] = random.randint(1, 20)
            data.dock_status.loc[random_index, 'Last Refresh'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Apply conditional formatting
            flagged_skus_df = data.dock_status.style.apply(flag_hot_sku, axis=1)   
            DOS_count_df =  fetch_DOS_count(data.dock_status)

            # Display dashboard sections
            st.markdown('### Urgent Items')
            st.altair_chart(DOS_count_df) 
            with col1:
                st.markdown('### Alerts')
                st.dataframe(data.alerts)
            with col2:
                st.markdown('### Dock Status')
                st.dataframe(flagged_skus_df)
            with col3:
                st.markdown('### Production Pipeline')
                st.dataframe(data.production_pipeline)

            time.sleep(2)

main()
