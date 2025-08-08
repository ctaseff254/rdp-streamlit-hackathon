import pandas as pd  # Pandas for data manipulation
import altair as alt  # Altair for charting
from pages.alerts import alert_severity_map  # Color mapping for alert severity
from db import WarehouseData  # Warehouse data structure (not used directly here)

def get_recs_with_eligible_DOS(df):
    """
    Returns a DataFrame of SKUs with Days of Service <= 7, grouped and counted by value.
    Args:
        df: DataFrame containing 'Days of Service' column.
    Returns:
        DataFrame with columns ['Days of Service', 'count'] for eligible SKUs.
    """
    # Count occurrences of each Days of Service value
    res = df["Days of Service"].value_counts().reset_index()
    # Filter for urgent SKUs (<= 7 days of service)
    res = res[res["Days of Service"] <= 7]
    return res

def fetch_DOS_count(dock_status):
    """
    Builds an Altair bar chart showing count of SKUs by Days of Service (<= 7).
    Args:
        dock_status: DataFrame containing dock status info.
    Returns:
        Altair Chart object for visualization in Streamlit.
    """
    # Prepare data for chart (only urgent SKUs)
    eligible_df = get_recs_with_eligible_DOS(dock_status)
    # Create Altair bar chart
    chart = alt.Chart(eligible_df).mark_bar(size=150).encode(
        x=alt.X('Days of Service', axis=alt.Axis(format='d')), # X-axis: Days of Service (integer)
        y=alt.Y('count', axis=alt.Axis(format='d')),           # Y-axis: count of SKUs
        color=alt.Color('Days of Service', 
                        scale=alt.Scale(range=list(alert_severity_map.values())[::-1])) # Color by severity
    )
    # Return chart for rendering in Streamlit
    return chart