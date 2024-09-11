# parse_statistics.py
import json
import os
import datetime
import mysql.connector
from mysql.connector import Error
import configparser
import pandas as pd
from sqlalchemy import create_engine

# Define the default statistics structure
default_stats = {
    "auctions_scraped": 0,
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0,
    "addresses_processed": 0,
    "addresses_updated": 0,
    "addresses_skipped": 0,
    "run_status": "success"
}

# List of expected statistics files with their paths
stats_files = [
    'publicsurplus/publicsurplus_statistics.json',
    'proxibid/proxibid_statistics.json',
    'hibid/hibid_statistics.json',
    'gsa/gsa_statistics.json',
    'govdeals/govdeals_statistics.json',
    'bidspotter/bidspotter_statistics.json',
    'smc/smc_statistics.json',
    'wisconsonsurplus/wisco_statistics.json',  # Added Wisconsin Surplus statistics file
    'backes/backes_statistics.json'  # Added Backes statistics file
]

# Function to ensure a statistics file exists
def ensure_stats_file(file_path):
    if not os.path.exists(file_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(default_stats, f)
        print(f"Created missing statistics file: {file_path}")

# Ensure all expected statistics files exist
for file in stats_files:
    ensure_stats_file(file)

# Aggregate statistics from all files
aggregated_stats = default_stats.copy()

for file in stats_files:
    with open(file, 'r') as f:
        stats = json.load(f)
        for key in aggregated_stats:
            aggregated_stats[key] += stats.get(key, 0)

# Add timestamp to aggregated statistics
aggregated_stats["timestamp"] = datetime.datetime.now().isoformat()

# Print aggregated statistics
print("\nAggregated Scraping Statistics:")
for key, value in aggregated_stats.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

# Save aggregated statistics to a JSON file
with open('aggregated_statistics.json', 'w') as f:
    json.dump(aggregated_stats, f, indent=2)

# Read database configuration from db.cfg
config = configparser.ConfigParser()
config.read('db.cfg')

db_config = {
    'host': config['mysql']['host'],
    'database': config['mysql']['database'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password']
}

# Create a SQLAlchemy engine
db_url = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
engine = create_engine(db_url)

# Function to check if the statistics table exists and create it if it doesn't
def ensure_statistics_table_exists():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    auctions_scraped INT,
                    items_added INT,
                    items_updated INT,
                    items_removed INT,
                    items_skipped INT,
                    errors INT,
                    addresses_processed INT,
                    addresses_updated INT,
                    addresses_skipped INT,
                    timestamp DATETIME
                )
            """)
            connection.commit()
            print("Ensured that the statistics table exists.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to insert aggregated statistics into the MySQL database
def insert_aggregated_statistics(stats):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO statistics (
                auctions_scraped, items_added, items_updated, items_removed, items_skipped, errors,
                addresses_processed, addresses_updated, addresses_skipped, timestamp, run_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                stats["auctions_scraped"], stats["items_added"], stats["items_updated"], stats["items_removed"],
                stats["items_skipped"], stats["errors"], stats["addresses_processed"], stats["addresses_updated"],
                stats["addresses_skipped"], stats["timestamp"], stats["run_status"]
            ))
            connection.commit()
            print("Aggregated statistics inserted into MySQL database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

# Ensure the statistics table exists
ensure_statistics_table_exists()

# Insert the aggregated statistics into the database
insert_aggregated_statistics(aggregated_stats)

# Function to calculate and print daily averages for all statistics
def calculate_daily_averages():
    try:
        with engine.connect() as connection:
            query = """
            SELECT 
                DATE(timestamp) as date,
                AVG(auctions_scraped) as avg_auctions_scraped,
                AVG(items_added) as avg_items_added,
                AVG(items_updated) as avg_items_updated,
                AVG(items_removed) as avg_items_removed,
                AVG(items_skipped) as avg_items_skipped,
                AVG(errors) as avg_errors,
                AVG(addresses_processed) as avg_addresses_processed,
                AVG(addresses_updated) as avg_addresses_updated,
                AVG(addresses_skipped) as avg_addresses_skipped,
                SUM(CASE WHEN run_status = 'error' THEN 1 ELSE 0 END) as error_count
            FROM statistics
            GROUP BY DATE(timestamp)
            """
            df = pd.read_sql(query, connection)
            print("\nDaily Averages:")
            print(df)
    except Exception as e:
        print(f"Error: {e}")

# Call the function to calculate daily averages
calculate_daily_averages()