import json
import mysql.connector
from mysql.connector import errorcode

# Database configuration details
db_config = {
    "user": "whatcheer",
    "password": "meatwad",
    "host": "localhost",
    "database": "auctions",
    "raise_on_warnings": True
}

# SQL to create the 'backes' table if it doesn't exist according to the updated schema
create_table_query = """
CREATE TABLE IF NOT EXISTS backes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    current_bid DECIMAL(10,2),
    lot_number VARCHAR(50) NOT NULL,
    time_left DATETIME,
    url VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    favorite CHAR(1),
    UNIQUE (item_name, lot_number)
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
    INSERT INTO backes (item_name, location, current_bid, lot_number, time_left, url, latitude, longitude, favorite)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id=id
    """
    for item in data:
        # Assuming some fields might be missing, we provide default values
        values = (
            item.get('item_name', ''),
            item.get('location', ''),
            item.get('current_bid', 0.0),
            item.get('lot_number', ''),
            item.get('time_left', None),
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
    json_file_path = 'auction_data.json'  # Ensure this is the correct path to your JSON file
    try:
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)
            all_items = []
            for key in json_data:
                if isinstance(json_data[key], list):
                    all_items.extend(json_data[key])

        cnx = connect_to_database(db_config)
        if cnx:
            ensure_table_exists(cnx)
            insert_data(cnx, all_items)
            cnx.close()
        else:
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
