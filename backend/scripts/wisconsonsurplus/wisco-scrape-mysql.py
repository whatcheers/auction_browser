import argparse
import json
import logging
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_mysql(config):
    try:
        connection = mysql.connector.connect(**config)
        logging.info("MySQL Database connection successful")
        return connection
    except Error as err:
        logging.error(f"Database connection error: {err}")
        return None

def ensure_table_exists(connection):
    table_name = "wiscosurp_auctions"
    cursor = connection.cursor()
    # Check if the table exists
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE `{table_name}` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `auction_number` VARCHAR(255),
        `lot_number` VARCHAR(50),
        `item_name` VARCHAR(500) NOT NULL,
        `url` TEXT,
        `time_left` DATETIME,
        `current_bid` DECIMAL(10,2),
        `location` VARCHAR(255),
        `latitude` FLOAT,
        `longitude` FLOAT,
        `favorite` CHAR(1) DEFAULT NULL
        )
        """
        cursor.execute(create_table_query)
        logging.info(f"Table '{table_name}' created.")
    else:
        logging.info(f"Table '{table_name}' already exists.")

    cursor.close()
    return table_name

def insert_item(connection, table_name, item):
    cursor = connection.cursor()
    insert_query = f"""
    INSERT INTO `{table_name}` (
    `auction_number`, `lot_number`, `item_name`, `url`, `time_left`, `current_bid`, `location`, `latitude`, `longitude`, `favorite`
    ) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """
    time_left = datetime.strptime(item['End Date'], '%Y-%m-%d %I:%M:%S %p')
    cursor.execute(insert_query, (
        item['Auction Number'],
        item['Lot Number'],
        item['Item Title'],
        item['Item URL'],
        time_left,
        item['Current Bid Amount'],
        item['Location Address'],
        item.get('latitude'),
        item.get('longitude'),
        None # Set the default value for the 'favorite' column to NULL
    ))
    connection.commit()
    logging.debug(f"Inserted item: {item['Item Title']}")
    cursor.close()

def main():
    parser = argparse.ArgumentParser(description='Import auction items into MySQL.')
    parser.add_argument('--file', type=str, help='JSON file containing auction items to import')
    parser.add_argument('--directory', type=str, help='Directory containing JSON files to import')
    args = parser.parse_args()

    config = {
        'user': 'whatcheer',
        'password': 'meatwad',
        'host': 'localhost',
        'database': 'auctions',
    }

    connection = connect_to_mysql(config)
    if not connection:
        logging.error("Exiting due to database connection failure.")
        return

    table_name = ensure_table_exists(connection)

    if args.directory:
        for filename in os.listdir(args.directory):
            if filename.startswith('auction_') and filename.endswith('.json'):
                file_path = os.path.join(args.directory, filename)
                with open(file_path, 'r') as file:
                    items = json.load(file)
                    for item in items:
                        insert_item(connection, table_name, item)
    elif args.file:
        with open(args.file, 'r') as file:
            items = json.load(file)
            for item in items:
                insert_item(connection, table_name, item)
    else:
        logging.error("Either --file or --directory argument is required.")

    connection.close()
    logging.info("Data import completed.")

if __name__ == "__main__":
    main()