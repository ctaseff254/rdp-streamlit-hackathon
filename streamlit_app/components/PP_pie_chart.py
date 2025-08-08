import altair as alt
import pandas as pd
from pages.alerts import alert_severity_map
import streamlit as st

def production_pipeline_pie_chart_altair(data, title='Production Status Overview', key=None):
    prod_status = data.production_pipeline['status']
    status_labels = ['Backlog', 'In Production', 'Ready to Ship']
    status_counts = [
        (prod_status == 'Backlog').sum(),
        (prod_status == 'In Production').sum(),
        (prod_status == 'Ready to Ship').sum()
    ]
    df = pd.DataFrame({
        'Status': status_labels,
        'Count': status_counts
    })
    chart = alt.Chart(df).mark_arc(innerRadius=0).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Status", type="nominal", scale=alt.Scale(range=alert_severity_map.values())),
        tooltip=['Status', 'Count']
    ).properties(
        title=title,
        width=300,
        height=300
    )
    st.altair_chart(chart, use_container_width=True, key=key)