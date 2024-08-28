import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_time_left(time_left_str):
    # Assuming time_left is in the format "MM/DD/YYYY hh:mm PM CT"
    # and that you want to ignore the "CT" timezone part for the parsing
    time_left_str_no_tz = " ".join(time_left_str.split()[:-1])  # Removes the timezone abbreviation
    return datetime.strptime(time_left_str_no_tz, '%m/%d/%Y %I:%M %p')

def connect_to_mysql(config):
    """Connect to the MySQL database and return the connection object."""
    try:
        connection = mysql.connector.connect(**config)
        logging.info("MySQL Database connection successful")
        return connection
    except Error as err:
        logging.error(f"Error connecting to MySQL: {err}")
        return None

def create_table_if_not_exists(connection):
    """Create the 'gsa' table if it doesn't exist."""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gsa (
id INT AUTO_INCREMENT PRIMARY KEY,
  item_name VARCHAR(255) NULL,
  location VARCHAR(255) NULL,
  current_bid DECIMAL(10,2) NULL,
  lot_number VARCHAR(50) UNIQUE NULL,
  time_left DATETIME NULL,
  url VARCHAR(255) NULL,
  favorite CHAR(1) NULL,
  latitude DECIMAL(11,8) NULL,
  longitude DECIMAL(12,8) NULL            )
        """)
        logging.info("Table 'gsa' created successfully.")
    except Error as err:
        logging.error(f"Error creating 'gsa' table: {err}")
    finally:
        cursor.close()

def insert_items(connection, items):
    cursor = connection.cursor(buffered=True)
    
    # Query to check if the item exists and get the current bid
    check_query = """
    SELECT current_bid, favorite FROM gsa WHERE item_name = %s AND lot_number = %s;
    """
    
    # Modified insert_query to insert or update depending on the condition
    insert_query = """
    INSERT INTO gsa (item_name, location, current_bid, lot_number, time_left, url, latitude, longitude, favorite)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
    location=VALUES(location), 
    current_bid=VALUES(current_bid),
    time_left=VALUES(time_left),
    url=VALUES(url),
    latitude=VALUES(latitude),
    longitude=VALUES(longitude),
    favorite=VALUES(favorite);
    """
    
    for item in items:
        try:
            # Check for existing item
            cursor.execute(check_query, (item.get('item_name', ''), item.get('lot_number', '')))
            existing = cursor.fetchone()
            
            # Parse time_left
            time_left = parse_time_left(item['time_left'])
            
            # Determine if we should update the existing record
            if existing is None or item.get('current_bid', 0) > existing[0]:
                cursor.execute(insert_query, (
                    item.get('item_name', ''),
                    item.get('location', ''),
                    item.get('current_bid', 0),
                    item.get('lot_number', ''),
                    time_left,
                    item.get('url', ''),
                    item.get('latitude', None),
                    item.get('longitude', None),
                    item.get('favorite', None)
                ))
            else:
                logging.info(f"Skipped inserting/updating item {item.get('item_name', '')} with lot number {item.get('lot_number', '')} due to not having a higher bid.")
                
        except Error as err:
            logging.error(f"Error inserting/updating item: {err}")
    
    connection.commit()
    logging.info("All items processed for insertion/update into the gsa table.")
    cursor.close()

def main(json_file_path):
    config = {
        'user': 'whatcheer',
        'password': 'meatwad',
        'host': 'localhost',
        'database': 'auctions',
    }

    # Connect to MySQL
    connection = connect_to_mysql(config)
    if not connection:
        return

    # Create the 'gsa' table if it doesn't exist
    create_table_if_not_exists(connection)

    # Load items from JSON file
    with open(json_file_path, 'r') as file:
        items = json.load(file)

    # Insert items into the database
    insert_items(connection, items)

    # Close the database connection
    connection.close()
    logging.info("Database connection closed.")

if __name__ == "__main__":
    json_file_path = 'auctionDetails.json'
    main(json_file_path)