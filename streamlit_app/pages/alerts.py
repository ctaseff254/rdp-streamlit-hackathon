from db import connect_to_db, WarehouseData
from datetime import datetime
import pandas as pd

alert_threshold = 7
alert_severity_map = {
    7: "#E2CE1E", 6: "#E2CE1E", 5: "#FD6104",
    4: "#FD6104", 3: "#FD0404", 2: "#FD0404", 1: "#FD0404"
}       

def add_new_alert(alert_id, sku_id, product_number, product_name, alert_type, alert_message, data: WarehouseData):
    connection, cursor = connect_to_db()
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_alert_df = pd.DataFrame([{'alert_id': alert_id, 
                                  'sku_id': sku_id,
                                  'product_number': product_number,
                                  'product_name': product_name, 
                                  'alert_type': alert_type, 
                                  'alert_message': alert_message, 
                                  'timestamp': current_timestamp}])
    
    data.alerts = pd.concat([data.alerts, new_alert_df], ignore_index=True)
    return data
    
def flag_hot_sku(row):
    """
    Flags a row in a DataFrame with a background color based on the 'Days of Service' value.

    If the 'Days of Service' is less than or equal to the alert threshold, the function applies
    a background color to each cell in the row based on a severity map. Otherwise, it returns
    an empty style for each cell.

    Parameters:
        row (pd.Series): A row from a pandas DataFrame containing a 'Days of Service' column.

    Returns:
        list: A list of style strings (e.g., 'background-color: #FD0404') for each cell in the row.
    """
    days_of_service = row['Days of Service']
    if days_of_service <= alert_threshold:
        color = alert_severity_map[int(days_of_service)]
        return [f'background-color: {color}'] * len(row)
    else:
        return [''] * len(row)
