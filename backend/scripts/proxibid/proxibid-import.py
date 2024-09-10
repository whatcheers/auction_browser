# Import required libraries
import json
import mysql.connector
import os
from datetime import datetime, timedelta
from colorama import Fore, Style
import glob

# Function to convert time left string to a datetime object
def convert_time_left(time_left):
    if time_left is None or time_left == 'N/A':
        return None
    
    days = 0
    hours = 0
    
    # Extract days and hours from the time_left string
    if 'Days' in time_left:
        days_part = time_left.split('Days')[0].strip()
        days = int(days_part)
    if 'Hours' in time_left:
        hours_part = time_left.split('Hours')[0].split()[-1].strip()
        hours = int(hours_part)
    
    # Calculate the future date based on the current date and time_left
    future_date = datetime.now() + timedelta(days=days, hours=hours)
    
    return future_date.strftime('%Y-%m-%d %H:%M:%S')

# Function to handle bid price formatting
def handle_bid_price(price):
    if price == 'N/A':
        return 0.00
    # Remove commas from the price string before converting to float
    price = price.replace(',', '')
    return float(price)

# Database configuration
config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

# SQL query to create the 'proxibid' table if it doesn't exist
create_table = """
CREATE TABLE IF NOT EXISTS auctions.proxibid (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lot_number VARCHAR(255) NOT NULL,
  item_name VARCHAR(255) NULL,
  url VARCHAR(255) UNIQUE,
  current_bid_price DECIMAL(10,2) NULL,
  location VARCHAR(255) NULL,
  time_left DATETIME NULL,
  auction_house VARCHAR(255) NULL,
  auction_title VARCHAR(255) NULL,
  favorite CHAR(1) DEFAULT NULL
);
"""

# SQL query to insert or update auction items
add_item = """
    INSERT INTO auctions.proxibid
    (lot_number, item_name, url, current_bid_price, location, time_left, auction_house, auction_title, favorite)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    item_name = VALUES(item_name),
    current_bid_price = VALUES(current_bid_price),
    location = VALUES(location),
    time_left = VALUES(time_left),
    auction_house = VALUES(auction_house),
    auction_title = VALUES(auction_title),
    favorite = VALUES(favorite)
"""

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
        with open('proxibid_statistics.json', 'r') as f:
            existing_stats = json.load(f)
        for key in stats:
            existing_stats[key] = (existing_stats.get(key, 0) or 0) + stats[key]
        with open('proxibid_statistics.json', 'w') as f:
            json.dump(existing_stats, f, indent=2)
    except FileNotFoundError:
        with open('proxibid_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)

def connect_to_db():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        return cnx, cursor
    except mysql.connector.Error as err:
        print(f"{Fore.RED}Error: {err}{Style.RESET_ALL}")
        return None, None

def create_proxibid_table(cursor, cnx):
    try:
        cursor.execute(create_table)
        print(f"{Fore.GREEN}Table 'proxibid' is ready.{Style.RESET_ALL}")
    except mysql.connector.Error as err:
        if err.errno == 1050:  # Error code for "Table already exists"
            print(f"{Fore.YELLOW}Table 'proxibid' already exists. Skipping creation.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Error creating table: {err}{Style.RESET_ALL}")
            cursor.close()
            cnx.close()
            exit(1)

def process_auction_data(cursor, auction_houses):
    for auction_house in auction_houses:
        for auction in auction_house.get('upcomingAuctions', []):
            for lot in auction.get('lots', []):
                try:
                    # Extract lot information
                    lot_number = lot.get('lot_number')
                    item_name = lot.get('item_name')
                    location = lot.get('location')
                    url = lot.get('url')
                    current_bid_price = handle_bid_price(lot.get('current_bid_price', 'N/A'))
                    time_left = convert_time_left(lot.get('time_left', 'N/A'))
                    auction_house_name = auction_house.get('name')
                    auction_title = auction.get('title')
                    favorite = None  # Assuming favorite is not provided in the JSON

                    # Prepare data and insert/update the database
                    data_item = (lot_number, item_name, url, current_bid_price, location, time_left, auction_house_name, auction_title, favorite)
                    cursor.execute(add_item, data_item)
                    if cursor.rowcount > 0:
                        if cursor.lastrowid:
                            stats["items_added"] += 1
                        else:
                            stats["items_updated"] += 1
                    else:
                        stats["items_skipped"] += 1
                    stats["auctions_scraped"] += len(auction_house.get('upcomingAuctions', []))
                except mysql.connector.Error as err:
                    print(f"{Fore.RED}Error inserting item: {lot}. Error: {err}{Style.RESET_ALL}")
                    stats["errors"] += 1
                except Exception as e:
                    print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
                    stats["errors"] += 1

def main():
    cnx, cursor = connect_to_db()
    if cnx is None or cursor is None:
        return

    create_proxibid_table(cursor, cnx)

    # Find the latest JSON file in the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_files = glob.glob(os.path.join(script_dir, 'iowa_auction_houses.json'))
    if json_files:
        latest_file = max(json_files, key=os.path.getctime)
        with open(latest_file) as json_file:
            auction_houses = json.load(json_file)
            process_auction_data(cursor, auction_houses)
            cnx.commit()
    else:
        print(f"{Fore.RED}No JSON files found in the directory.{Style.RESET_ALL}")

    # Close database connections
    cursor.close()
    cnx.close()

    # Print summary of the operation
    print(f"{Fore.GREEN}Items added: {stats['items_added']}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Items updated: {stats['items_updated']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Items skipped: {stats['items_skipped']}{Style.RESET_ALL}")
    print(f"{Fore.RED}Errors: {stats['errors']}{Style.RESET_ALL}")

    # Save statistics
    update_statistics()

if __name__ == "__main__":
    main()
