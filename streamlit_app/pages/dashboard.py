import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import sys
import os
import threading, time
import random
import altair as alt
from pages.alerts import flag_hot_sku, alert_severity_map, add_new_alert # 2nd import is temporary
from components.DOS_bar_chart import fetch_DOS_count
from components.PP_pie_chart import production_pipeline_pie_chart_altair
from db import get_all_data, WarehouseData
import numpy as np

def real_time_update(warehouse_data: WarehouseData):
    random_row = warehouse_data.dock_status.sample(n=1)
    random_index = random_row.index[0]

    current_random_row = warehouse_data.dock_status.iloc[random_index]
    
    if current_random_row['Days of Service'] - 1 == 7:
        new_index = warehouse_data.alerts['alert_id'].max() + 1
        warehouse_data = add_new_alert(new_index, 
                                       current_random_row['sku_id'],
                                       current_random_row['Product Number'],
                                       current_random_row['Product Name'], 
                                       'Urgent SKU', 
                                       'Low days of service', 
                                       warehouse_data)
        
    warehouse_data.dock_status.loc[random_index, 'Days of Service'] = current_random_row['Days of Service'] - 1 if current_random_row['Days of Service'] > 1 else 50
    warehouse_data.dock_status.loc[random_index, 'Last Refresh'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    warehouse_data.dock_status['Dock Aging Hours'] = [int((datetime.now() - time_created).total_seconds() // 3600) for time_created in warehouse_data.dock_status['Time Created']]
    return warehouse_data

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
            # Apply conditional formatting
            flagged_skus_df = data.dock_status.style.apply(flag_hot_sku, axis=1) 
            
            DOS_count_df =  fetch_DOS_count(data.dock_status)

            data = real_time_update(data)
           
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
