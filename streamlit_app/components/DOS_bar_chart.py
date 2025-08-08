import pandas as pd
import altair as alt
from pages.alerts import alert_severity_map
from db import WarehouseData

def get_recs_with_eligible_DOS(df):
    res = df["Days of Service"].value_counts().reset_index()
    res = res[res["Days of Service"] <= 7]
    return res

def fetch_DOS_count(dock_status):
    chart = alt.Chart(get_recs_with_eligible_DOS(dock_status)).mark_bar(size=150).encode(
        x=alt.X('Days of Service', axis=alt.Axis(format='d')), # 'd' for integer format
        y=alt.Y('count', axis=alt.Axis(format='d')),
        color=alt.Color('Days of Service', 
                        scale=alt.Scale(range=list(alert_severity_map.values())[::-1]))
    )

    return chart