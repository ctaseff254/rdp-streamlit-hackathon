import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import sys
import os
import threading, time
import random
import numpy as np
from pages.alerts import flag_hot_sku
from components.DOS_bar_chart import fetch_DOS_count
from components.PP_pie_chart import production_pipeline_pie_chart_altair
from db import get_all_data, WarehouseData

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return f'{val}'
    return my_autopct
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
    st.sidebar.title("Home")
    hidden = st.sidebar.checkbox("Hide graphs")
    st.sidebar.button("SKUs")
    st.sidebar.button("Lanes")
    st.sidebar.button("Orders")
    st.sidebar.button("Settings")
    st.set_page_config(
        page_title="Real-time Dock Status Dashboard",
        page_icon="📦",
        layout="wide",
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        urgency_filter = st.selectbox('Select urgency', options=['All', 'Urgent', 'Not-Urgent'])
    with filter_col2:
        dock_filter = st.selectbox('Select dock location', options=np.insert(data.dock_status['Dock Location'].unique(), 0, 'All'))
    with filter_col3:
        destination_filter = st.selectbox('Select destination',
                                options=np.insert(data.dock_status['Destination'].unique(), 0, 'All')) 
    
    st.title("Dock Status Dashboard")  
    placeholder = st.empty()

    # Real-time data simulation loop
    while True:
        with placeholder.container():
            if not hidden:
                pie, bar = st.columns(2)
                with bar:
                    DOS_count_df = fetch_DOS_count(data.dock_status)

                    # Display dashboard sections
                    st.markdown('### Urgent Items')
                    st.altair_chart(DOS_count_df)
                with pie:
                    production_pipeline_pie_chart_altair(data)

            # Randomize 'Days of Service' for a random SKU
            random_row = data.dock_status.sample(n=1)
            random_index = random_row.index[0]
            current_days_of_service = data.dock_status.loc[random_index, 'Days of Service']

            data.dock_status.loc[random_index, 'Days of Service'] = current_days_of_service - 1 if current_days_of_service > 1 else 99
            data.dock_status.loc[random_index, 'Last Refresh'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            col1, col2 = st.columns([1, 3])
        
            # Display dashboard sections
            with col1:
                st.markdown('### 🔔 Alerts')
                st.dataframe(data.alerts)
            with col2:
                st.markdown('### 📤 SKU Status')                
                # Apply conditional formatting
                
                filtered_df = data.dock_status
                
                if destination_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Destination'] == destination_filter]
                if dock_filter != 'All':
                    filtered_df = filtered_df[filtered_df['Dock Location'] == dock_filter]
                    
                if urgency_filter == 'Urgent':
                    filtered_df = filtered_df[filtered_df['Days of Service'] <= 7]
                elif urgency_filter == 'Not-Urgent':
                    filtered_df = filtered_df[filtered_df['Days of Service'] > 7]

                flagged_skus_df = filtered_df.style.apply(flag_hot_sku, axis=1)   
                st.dataframe(flagged_skus_df)

            time.sleep(2)

main()
