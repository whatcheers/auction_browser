import mysql.connector
from mysql.connector import Error
import json
import re
from datetime import datetime
import logging
import os

# ANSI color codes for console output
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Initialize logging
logging.basicConfig(filename='auctions.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize statistics
stats = {
    "auctions_scraped": 0,
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0,
    "addresses_processed": 0,
    "addresses_updated": 0,
    "addresses_skipped": 0
}

def update_statistics():
    try:
        with open('wisco_statistics.json', 'r') as f:
            existing_stats = json.load(f)
        for key in stats:
            existing_stats[key] = (existing_stats.get(key, 0) or 0) + stats[key]
        with open('wisco_statistics.json', 'w') as f:
            json.dump(existing_stats, f, indent=2)
    except FileNotFoundError:
        with open('wisco_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)

def create_tables(connection):
    """Create the necessary tables if they don't exist."""
    try:
        with connection.cursor() as cursor:
            # Create upcoming_wisco_list table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upcoming_wisco_list (
                    auction_number VARCHAR(20),
                    auction_name VARCHAR(255),
                    location VARCHAR(255),
                    auction_closing_date DATETIME,
                    url_for_auction_details VARCHAR(255),
                    url_to_view_items VARCHAR(255),
                    processed TINYINT(1) DEFAULT 0
                )
            """)
            print(f"{colors.OKGREEN}Table 'upcoming_wisco_list' is ready.{colors.ENDC}")
            logging.info("Table 'upcoming_wisco_list' is ready.")

            # Create wiscosurp_auctions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wiscosurp_auctions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    auction_number VARCHAR(255) NULL,
                    lot_number VARCHAR(50) NULL,
                    item_name VARCHAR(255) NULL,
                    url VARCHAR(500) NULL,
                    time_left DATETIME NULL,
                    current_bid DECIMAL(10,2) NULL,
                    location VARCHAR(255) NULL,
                    latitude DECIMAL(11,8) NULL,
                    longitude DECIMAL(12,8) NULL,
                    favorite CHAR(1) NULL
                )
            """)
            print(f"{colors.OKGREEN}Table 'wiscosurp_auctions' is ready.{colors.ENDC}")
            logging.info("Table 'wiscosurp_auctions' is ready.")

    except Error as create_table_error:
        print(f"{colors.FAIL}Error creating tables: {create_table_error}{colors.ENDC}")
        logging.error(f"Error creating tables: {create_table_error}")
        stats["errors"] += 1

def check_and_insert_auctions_data(connection, json_file_path):
    """Check for existing data and insert new auction data."""
    try:
        if not os.path.exists(json_file_path):
            print(f"{colors.FAIL}Error: {json_file_path} not found. Creating an empty file.{colors.ENDC}")
            open(json_file_path, 'w').close()  # Create an empty file

        with open(json_file_path, 'r') as file:
            auctions_data = json.load(file)

        if auctions_data:
            with connection.cursor() as cursor:
                # Check for duplicate auction numbers
                cursor.execute("""
                    SELECT auction_number
                    FROM upcoming_wisco_list
                """)
                existing_auction_numbers = [row[0] for row in cursor.fetchall()]

                for item in auctions_data:
                    if item['Auction Number'] not in existing_auction_numbers:
                        formatted_date = format_auction_closing_date(item['Auction Closing Date'])
                        cursor.execute("""
                            INSERT INTO upcoming_wisco_list (auction_number, auction_name, location, auction_closing_date, url_for_auction_details, url_to_view_items, processed)
                            VALUES (%s, %s, %s, %s, %s, %s, 0)
                        """, (item['Auction Number'], item['Auction Name'], item['Location'], formatted_date, item['URL for Auction Details'], item['URL to View Items']))

                        print(f"{colors.OKBLUE}Processed auction: {item['Auction Number']} - {item['Auction Name']}{colors.ENDC}")
                        logging.info(f"Auction processed: {item['Auction Number']} - {item['Auction Name']}")
                        stats["auctions_scraped"] += 1
                    else:
                        print(f"{colors.WARNING}Skipped duplicate auction: {item['Auction Number']} - {item['Auction Name']}{colors.ENDC}")
                        logging.warning(f"Skipped duplicate auction: {item['Auction Number']} - {item['Auction Name']}")
                        stats["items_skipped"] += 1

            connection.commit()
            print(f"{colors.OKGREEN}All data inserted/verified successfully.{colors.ENDC}")
            logging.info("All data inserted/verified successfully.")
        else:
            print(f"{colors.WARNING}No auction data found in {json_file_path}.{colors.ENDC}")
            logging.warning(f"No auction data found in {json_file_path}.")
            stats["errors"] += 1

    except Error as process_auctions_error:
        print(f"{colors.FAIL}Error while processing auctions data: {process_auctions_error}{colors.ENDC}")
        logging.error(f"Error while processing auctions data: {process_auctions_error}")
        stats["errors"] += 1

def format_auction_closing_date(date_str):
    """Convert auction closing date to MySQL DATETIME format."""
    formatted_date_str = re.sub(r'(st|nd|rd|th)', '', date_str)
    date_obj = datetime.strptime(formatted_date_str, "%b %d, %Y %I:%M %p")
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main function to establish database connection and process auctions data."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='whatcheer',
            password='meatwad',
            database='auctions'  # Directly specify the existing database here
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"{colors.OKGREEN}MySQL Database connection successful. MySQL Server version on {db_info}{colors.ENDC}")
            logging.info(f"MySQL Database connection successful. MySQL Server version on {db_info}")
            
            create_tables(connection)
            check_and_insert_auctions_data(connection, 'auctions_data.json')
    
    except Error as mysql_connection_error:
        print(f"{colors.FAIL}Error while connecting to MySQL: {mysql_connection_error}{colors.ENDC}")
        logging.error(f"Error while connecting to MySQL: {mysql_connection_error}")
        stats["errors"] += 1
    finally:
        if connection.is_connected():
            connection.close()
            print(f"{colors.OKBLUE}MySQL connection is closed{colors.ENDC}")
            logging.info("MySQL connection is closed")

    # Save statistics
    update_statistics()

    logging.info(f"{Fore.BLUE}Wisconsin Surplus List Statistics:{Style.RESET_ALL}")
    logging.info(f"Auctions scraped: {stats['auctions_scraped']}")
    logging.info(f"Items added: {stats['items_added']}")
    logging.info(f"Items updated: {stats['items_updated']}")
    logging.info(f"Items skipped: {stats['items_skipped']}")
    logging.info(f"Errors: {stats['errors']}")

if __name__ == "__main__":
    main()