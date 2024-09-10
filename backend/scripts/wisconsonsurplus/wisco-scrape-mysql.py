import argparse
import json
import logging
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
from colorama import init, Fore, Style

# Initialize colorama
init()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize statistics
stats = {
    "items_added": 0,
    "items_updated": 0,
    "items_skipped": 0,
    "items_removed": 0,
    "errors": 0
}

def connect_to_mysql(config):
    try:
        connection = mysql.connector.connect(**config)
        logging.info(f"{Fore.GREEN}MySQL Database connection successful{Style.RESET_ALL}")
        return connection
    except Error as err:
        logging.error(f"{Fore.RED}Database connection error: {err}{Style.RESET_ALL}")
        stats["errors"] += 1
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
        logging.info(f"{Fore.GREEN}Table '{table_name}' created.{Style.RESET_ALL}")
    else:
        logging.info(f"{Fore.YELLOW}Table '{table_name}' already exists.{Style.RESET_ALL}")

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
    logging.debug(f"{Fore.GREEN}Inserted item: {item['Item Title']}{Style.RESET_ALL}")
    cursor.close()
    stats["items_added"] += 1

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
        logging.error(f"{Fore.RED}Exiting due to database connection failure.{Style.RESET_ALL}")
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
        logging.error(f"{Fore.RED}Either --file or --directory argument is required.{Style.RESET_ALL}")
        stats["errors"] += 1

    connection.close()
    logging.info(f"{Fore.GREEN}Data import completed.{Style.RESET_ALL}")

    # Save statistics
    with open('wisco_mysql_statistics.json', 'w') as f:
        json.dump(stats, f)

    logging.info(f"{Fore.BLUE}Wisconsin Surplus MySQL Statistics:{Style.RESET_ALL}")
    logging.info(f"Items added: {stats['items_added']}")
    logging.info(f"Items updated: {stats['items_updated']}")
    logging.info(f"Items skipped: {stats['items_skipped']}")
    logging.info(f"Items removed: {stats['items_removed']}")
    logging.info(f"Errors: {stats['errors']}")

if __name__ == "__main__":
    main()