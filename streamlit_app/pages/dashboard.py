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
from streamlit_extras.stylable_container import stylable_container
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
        
    warehouse_data.dock_status.loc[random_index, 'Days of Service'] = current_random_row['Days of Service'] - 1 if current_random_row['Days of Service'] > 1 else 20
    warehouse_data.dock_status.loc[random_index, 'Last Refresh'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    warehouse_data.dock_status['Dock Aging Hours'] = [int((datetime.now() - time_created).total_seconds() // 3600) for time_created in warehouse_data.dock_status['Time Created']]
    return warehouse_data

def main():
    """
    Launches a real-time Streamlit dashboard for monitoring dock status and SKU alerts.
    """

    # Retrieve all warehouse data (SKUs, dock status, alerts, etc.)
    data = get_all_data()

    # Sidebar navigation buttons for switching dashboard views
    home = st.sidebar.button("Home")
    sku_view = st.sidebar.button("SKUs")  # Show SKU table only
    lane_view = st.sidebar.button("Lanes")  # Show dock status table only
    pp_view = st.sidebar.button("Production Pipeline")  # Show production pipeline table only
        # Load warehouse data
        

    st.set_page_config(
        page_title="Real-time Dock Status Dashboard",
        page_icon="📦",
        
        # Sidebar navigation buttons
        layout="wide",
    )

    def side_buttons():
        with stylable_container(
            key="sidebar_buttons",
        
        # Set Streamlit page config
            css_styles="""
                button {
                    background-color: green;
                    color: white;
                    border-radius: 10px;
                    margin-bottom: 12px;
                }
            """,
        ):
            st.empty()

    # Render stylable sidebar buttons and custom settings button
    with st.sidebar:
        side_buttons()

    # Custom HTML/CSS for a styled settings button at the bottom of the sidebar
    with st.sidebar:
        st.markdown("""
            <style>
            .settings-button-container button {
                background-color: green;
                color: white;
                border-radius: 10px;
                width: 100%;
                padding: 0.5em 1em;
                font-weight: bold;
                border: none;
                bottom:0;
            }
            </style>
            <div class="settings-button-container">
                <button type>⚙️ Settings</button>
            </div>
        """, unsafe_allow_html=True)

    # Three filter columns for urgency, dock location, and destination
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        # Filter by urgency (affects dock status table)
        urgency_filter = st.selectbox('Select urgency', options=['All', 'Urgent', 'Not-Urgent'])
    with filter_col2:
        # Filter by dock location (affects dock status table)
        dock_filter = st.selectbox('Select dock location', options=np.insert(data.dock_status['Dock Location'].unique(), 0, 'All'))
    with filter_col3:
        # Filter by destination (affects dock status table)
        destination_filter = st.selectbox('Select destination', options=np.insert(data.dock_status['Destination'].unique(), 0, 'All'))

    # Main dashboard title and placeholder for dynamic content
    st.title("Dock Status Dashboard")
    placeholder = st.empty()

    # Conditional views for sidebar navigation
    if sku_view:
        # Show only SKU table if SKU button pressed
        st.markdown('### SKU Overview')
        st.dataframe(data.skus)
    elif lane_view:
        # Show only dock status table if Lane button pressed
        st.markdown('### Dock Overview')
        st.dataframe(data.dock_status)
    elif pp_view:
        # Show only production pipeline table if Production Pipeline button pressed
        st.markdown('### Production Pipeline Overview')
        st.dataframe(data.production_pipeline)
    else:
        # Main dashboard with real-time updates and charts
        hidden = st.sidebar.checkbox("Hide graphs")
        while True:
            with placeholder.container():
                if not hidden:
                    # Top row: urgent items bar chart and production pipeline pie chart
                    pie, bar = st.columns(2)
                    with bar:
                        # Display urgent items bar chart (Altair)
                        DOS_count_df = fetch_DOS_count(data.dock_status)
                        st.markdown('### Urgent Items')
                        st.altair_chart(DOS_count_df)
                    with pie:
                        # Display production pipeline pie chart (Altair)
                        production_pipeline_pie_chart_altair(data)
                # Simulate real-time update of Days of Service for a random SKU
                random_row = data.dock_status.sample(n=1)
                random_index = random_row.index[0]
                current_days_of_service = data.dock_status.loc[random_index, 'Days of Service']
                # Decrement Days of Service, reset to 99 if it reaches 1
                data.dock_status.loc[random_index, 'Days of Service'] = current_days_of_service - 1 if current_days_of_service > 1 else 99
                # Update last refresh timestamp for the SKU
                data.dock_status.loc[random_index, 'Last Refresh'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Apply conditional formatting to dock status
                flagged_skus_df = data.dock_status.style.apply(flag_hot_sku, axis=1)
                # Second row: alerts and filtered dock status table
                col1, col2 = st.columns({1, 3})
                with col1:
                    # Display alerts table
                    st.markdown('### Alerts')
                    st.dataframe(data.alerts)
                with col2:
                    # Display dock status table with applied filters
                    st.markdown('### Dock Status')
                    filtered_df = data.dock_status
                    # Apply filters for destination, dock location, and urgency to dock status
                    if destination_filter != 'All':
                        filtered_df = filtered_df[data.dock_status['Destination'] == destination_filter]
                    if dock_filter != 'All':
                        filtered_df = filtered_df[filtered_df['Dock Location'] == dock_filter]
                    if urgency_filter == 'Urgent':
                        filtered_df = filtered_df[filtered_df['Days of Service'] <= 7]
                    elif urgency_filter == 'Not-Urgent':
                        filtered_df = filtered_df[filtered_df['Days of Service'] > 7]
                    # Apply conditional formatting to filtered dock status
                    flagged_skus_df = filtered_df.style.apply(flag_hot_sku, axis=1)
                    st.dataframe(flagged_skus_df)

                # Loop every 2 seconds to simulate real-time dashboard
                time.sleep(5)

main()
