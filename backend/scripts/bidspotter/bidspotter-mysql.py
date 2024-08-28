import json
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import os

# Database configuration details
db_config = {
    "user": "whatcheer",
    "password": "meatwad",
    "host": "localhost",
    "database": "auctions",
    "raise_on_warnings": True
}

# SQL to create the 'bidspotter' table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS bidspotter (
id INT AUTO_INCREMENT PRIMARY KEY,
  item_name VARCHAR(255) NULL,
  location VARCHAR(255) NULL,
  current_bid DECIMAL(10,2) NULL,
  lot_number VARCHAR(50) UNIQUE NULL,
  time_left DATETIME NULL,
  url VARCHAR(255) NULL,
  favorite CHAR(1) NULL,
  latitude DECIMAL(11,8) NULL,
  longitude DECIMAL(12,8) NULL
)"""

def connect_to_database(config):
    print("Attempting to connect to the database...")
    try:
        cnx = mysql.connector.connect(**config)
        print("Successfully connected to the database.")
        return cnx
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
    return None

def ensure_table_exists(cnx):
    print("Checking for table existence...")
    cursor = cnx.cursor()
    try:
        cursor.execute(create_table_query)
        print("Table checked/created according to the updated schema.")
    except mysql.connector.Error as err:
        print(f"Error checking/creating table: {err}")
    finally:
        cnx.commit()
        cursor.close()

def insert_data(cnx, data):
    print("Inserting data...")
    cursor = cnx.cursor()
    insert_query = """
    INSERT INTO bidspotter (item_name, location, current_bid, lot_number, time_left, url, latitude, longitude, favorite)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id
    """
    for item in data:
        # Format the time_left field
        time_left = None
        if item.get('time_left'):
            time_left_str = item['time_left'].strip()
            if time_left_str.startswith('Bidding opens'):
                time_left = datetime.strptime(time_left_str.replace('Bidding opens', '').strip(), '%d %b').replace(year=2024)
            elif time_left_str.startswith('Bidding ends:'):
                time_left = datetime.strptime(time_left_str.replace('Bidding ends:', '').strip(), '%d %b').replace(year=2024)
            else:
                print(f"Unsupported time_left format for item '{item.get('item_name', '')}': {time_left_str}")
                continue

        # Assuming some fields might be missing, we provide default values
        values = (
            item.get('item_name', ''),
            item.get('location', ''),
            item.get('current_bid', 0.0),
            item.get('lot_number', ''),
            time_left,
            item.get('url', None),
            item.get('latitude', None),
            item.get('longitude', None),
            item.get('favorite', None)
        )
        try:
            cursor.execute(insert_query, values)
            print(f"Inserted or updated item: {item.get('item_name', '')}")
        except mysql.connector.Error as err:
            print(f"Failed to insert item {item.get('item_name', '')}: {err}")
    cnx.commit()
    cursor.close()

if __name__ == "__main__":
    print("Script execution started.")
    json_file_path = 'auction-details.json'  # Ensure this is the correct path to your JSON file

    # Touch the file to ensure it exists
    open(json_file_path, 'a').close()

    try:
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        if json_data:
            cnx = connect_to_database(db_config)
            if cnx:
                ensure_table_exists(cnx)
                insert_data(cnx, json_data)
                cnx.close()
            else:
                print("Failed to connect to the database.")
        else:
            print(f"Error: {json_file_path} is empty or contains invalid data.")
    except FileNotFoundError:
        print(f"Error: {json_file_path} not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data in {json_file_path} - {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
