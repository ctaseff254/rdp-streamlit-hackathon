import altair as alt  # Altair for charting
import pandas as pd  # Pandas for data manipulation
from pages.alerts import alert_severity_map  # (Unused here, but imported for possible future severity mapping)
import streamlit as st  # Streamlit for UI rendering

def production_pipeline_pie_chart_altair(data, title='Production Status Overview', key=None):
    """
    Renders a pie chart summarizing the production pipeline status using Altair and Streamlit.
    Args:
        data: WarehouseData object containing production_pipeline DataFrame.
        title: Title for the chart.
        key: Optional Streamlit key for widget uniqueness.
    """
    # Extract status column from production pipeline data
    prod_status = data.production_pipeline['status']
    # Define possible status labels for the pie chart
    status_labels = ['Backlog', 'In Production', 'Ready to Ship']
    # Count occurrences of each status
    status_counts = [
        (prod_status == 'Backlog').sum(),
        (prod_status == 'In Production').sum(),
        (prod_status == 'Ready to Ship').sum()
    ]
    # Build DataFrame for charting
    df = pd.DataFrame({
        'Status': status_labels,
        'Count': status_counts
    })
    # Create Altair pie chart (arc) with color and tooltips
    chart = alt.Chart(df).mark_arc(innerRadius=0).encode(
        theta=alt.Theta(field="Count", type="quantitative"),  # Pie slice size by count
        color=alt.Color(field="Status", type="nominal"),      # Color by status
        tooltip=['Status', 'Count']                             # Show status/count on hover
    ).properties(
        title=title,
        width=300,
        height=300
    )
    # Render chart in Streamlit app, using container width and optional key
    st.altair_chart(chart, use_container_width=True, key=key)