import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import random

database_file = 'warehouse_data.db'

class WarehouseData:
    """
    A container class for storing various warehouse-related datasets.

    Attributes:
        alerts (pd.DataFrame): DataFrame containing alert information.
        skus (pd.DataFrame): DataFrame containing SKU details for alerted SKUs.
        dock_status (pd.DataFrame): DataFrame containing dock status information.
        skus_all (pd.DataFrame): DataFrame containing all SKU records.
        production_pipeline (pd.DataFrame): DataFrame containing production pipeline data.
    """
    def __init__(self, alerts: pd.DataFrame=None, skus: pd.DataFrame=None,
                 dock_status: pd.DataFrame=None, skus_all: pd.DataFrame=None,
                 production_pipeline: pd.DataFrame=None):
        self.alerts = alerts
        self.skus = skus
        self.dock_status = dock_status
        self.skus_all = skus_all
        self.production_pipeline = production_pipeline

def random_time(start, end):
        """Generate a random datetime between `start` and `end`."""
        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

def connect_to_db():
    """
    Establishes a connection to the SQLite database.

    Returns:
        tuple: A tuple containing the SQLite connection object and cursor.
    """
    connection = sqlite3.connect(database_file)
    c = connection.cursor()
    return connection, c

def get_all_data():
    """
    Retrieves and processes all relevant warehouse data from the database.

    This function:
    - Connects to the SQLite database.
    - Queries multiple tables: alerts, skus, dock_status, skus_all, and production_pipeline.
    - Joins and formats the dock_status data for display.
    - Converts date strings to datetime objects and renames columns for clarity.
    - Returns a WarehouseData object containing all the retrieved DataFrames.

    Returns:
        WarehouseData: An object containing all the warehouse-related datasets.
    """
    conn_ref, cursor = connect_to_db()
    
    alerts_df = pd.read_sql_query('SELECT * FROM alerts;', conn_ref)

    skus_df = pd.read_sql('SELECT * FROM skus WHERE sku_id IN (SELECT sku_id FROM alerts);', conn_ref)
    
    dock_status_df = pd.read_sql("""
        SELECT 
            s.product_number, 
            s.product_name,
            d.staging_lane, 
            d.dock_location, 
            d.last_refresh, 
            d.days_of_service,
            s.destination, 
            s.remortgage_gallons, 
            s.pallets, 
            s.weight_lbs 
        FROM dock_status AS d
        INNER JOIN skus AS s ON d.sku_id = s.sku_id
    """, conn_ref)

    dock_status_df['last_refresh'] = pd.to_datetime(dock_status_df['last_refresh'], format='%Y-%m-%d %H:%M:%S')
    dock_status_df['days_of_service'].astype(int)

    # Define your time range and random time in that range
    start_time = datetime.strptime("2025-08-01 03:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime("2025-08-07 23:59:59", "%Y-%m-%d %H:%M:%S")
    rand_time = random_time(start_time, end_time)
    dock_status_df["Time Created"] = [random_time(start_time, end_time) for row in range(len(dock_status_df))]

    dock_status_df.rename(columns={
        'staging_lane': 'Staging Lane', 
        'dock_location': 'Dock Location', 
        'last_refresh': 'Last Refresh',
        'product_name': 'Product Name',
        'product_number': 'Product Number',
        'days_of_service': 'Days of Service',
        'dock_aging_hours': 'Dock Aging Hours',
        'destination': 'Destination',
        'remortgage_gallons': 'Remortgage Gallons',
        'pallets': 'Pallets',
        'weight_lbs': 'Weight (lbs)',
    }, inplace=True)

    skus_all_df = pd.read_sql('SELECT * FROM skus;', conn_ref)
    production_pipeline_df = pd.read_sql('SELECT * FROM production_pipeline;', conn_ref)

    data = WarehouseData(alerts_df, skus_df, dock_status_df, skus_all_df, production_pipeline_df)
    
    return data
