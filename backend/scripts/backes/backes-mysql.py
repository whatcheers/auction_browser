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
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) AS new_values
    ON DUPLICATE KEY UPDATE
    current_bid = new_values.current_bid,
    time_left = new_values.time_left
    """
    items_added = 0
    items_updated = 0
    for item in data:
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
            if cursor.rowcount == 1:
                items_added += 1
                print(f"Inserted new item: {item.get('item_name', '')}")
            elif cursor.rowcount == 2:
                items_updated += 1
                print(f"Updated item: {item.get('item_name', '')}")
        except mysql.connector.Error as err:
            if err.errno == 1406:  # Data too long error
                print(f"Data too long for item {item.get('item_name', '')}. Truncating data.")
                truncated_values = list(values)
                for i, val in enumerate(truncated_values):
                    if isinstance(val, str):
                        truncated_values[i] = val[:255]  # Truncate to 255 characters
                try:
                    cursor.execute(insert_query, tuple(truncated_values))
                    if cursor.rowcount == 1:
                        items_added += 1
                        print(f"Inserted new item (truncated): {item.get('item_name', '')}")
                    elif cursor.rowcount == 2:
                        items_updated += 1
                        print(f"Updated item (truncated): {item.get('item_name', '')}")
                except mysql.connector.Error as err:
                    print(f"Failed to insert/update item {item.get('item_name', '')} even after truncation: {err}")
            else:
                print(f"Failed to insert/update item {item.get('item_name', '')}: {err}")
    cnx.commit()
    cursor.close()
    return items_added, items_updated

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
            items_added, items_updated = insert_data(cnx, all_items)
            cnx.close()
            
            # Save statistics
            with open('backes_statistics.json', 'w') as f:
                json.dump({
                    "auctions_scraped": 1,  # Assuming one auction is scraped per run
                    "items_added": items_added,
                    "items_updated": items_updated,
                    "items_removed": 0,
                    "items_skipped": 0,
                    "errors": 0,
                    "addresses_processed": 0,
                    "addresses_updated": 0,
                    "addresses_skipped": 0
                }, f)
            
            print(f"Statistics saved: {items_added} items added, {items_updated} items updated")
        else:
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"An error occurred: {e}")
