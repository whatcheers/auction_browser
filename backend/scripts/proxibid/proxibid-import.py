# Import required libraries
import json
import mysql.connector
import os
from datetime import datetime, timedelta
from colorama import Fore, Style
import glob
import subprocess

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

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))


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
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) AS new
    ON DUPLICATE KEY UPDATE
    item_name = new.item_name,
    current_bid_price = new.current_bid_price,
    location = new.location,
    auction_house = new.auction_house,
    auction_title = new.auction_title,
    favorite = new.favorite,
    auctions.proxibid.time_left = IF(new.time_left <> auctions.proxibid.time_left, new.time_left, auctions.proxibid.time_left)
"""


# Initialize counters and lists for tracking progress
successful_items = 0
duplicate_items = 0
skipped_items = []

# Attempt to connect to the database
try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
except mysql.connector.Error as err:
    print(f"{Fore.RED}Error connecting to the database: {err}{Style.RESET_ALL}")
    exit(1)

# Check if the 'proxibid' table exists, create it if it doesn't
try:
    cursor.execute("SHOW TABLES IN auctions LIKE 'proxibid'")
    if not cursor.fetchone():
        cursor.execute(create_table)
        print(f"{Fore.GREEN}Table 'auctions.proxibid' created.{Style.RESET_ALL}")
except mysql.connector.Error as err:
    print(f"{Fore.RED}Error checking or creating the 'proxibid' table: {err}{Style.RESET_ALL}")
    cursor.close()
    cnx.close()
    exit(1)

# Find the latest JSON file in the script directory
json_files = glob.glob(os.path.join(script_dir, 'iowa_auction_houses.json'))
if json_files:
    latest_file = max(json_files, key=os.path.getctime)
    with open(latest_file) as json_file:
        auction_houses = json.load(json_file)

        # Process each auction house, auction, and lot
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

                        # Prepare data and insert/update the database
                        data_item = (lot_number, item_name, url, current_bid_price, location, time_left, auction_house_name, auction_title)
                        cursor.execute(add_item, data_item)
                        successful_items += 1
                    except mysql.connector.Error as err:
                        print(f"{Fore.RED}Error inserting item: {lot}. Error: {err}{Style.RESET_ALL}")
                        skipped_items.append(lot)
                    except Exception as e:
                        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
                        skipped_items.append(lot)

        # Commit the changes to the database
        cnx.commit()

# Close database connections
cursor.close()
cnx.close()

# Print summary of the operation
print(f"{Fore.GREEN}Successful insertions: {successful_items}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Duplicate items: {duplicate_items}{Style.RESET_ALL}")
print(f"{Fore.RED}Skipped items: {len(skipped_items)}{Style.RESET_ALL}")

# Run the proxibid-latlong.py script
try:
    subprocess.run(["python3", "proxibid-latlong.py"], check=True)
    print(f"{Fore.GREEN}proxibid-latlong.py script executed successfully.{Style.RESET_ALL}")
except FileNotFoundError:
    print(f"{Fore.RED}proxibid-latlong.py script not found. Please check the file path.{Style.RESET_ALL}")
except subprocess.CalledProcessError as e:
    print(f"{Fore.RED}Error occurred while running proxibid-latlong.py: {e}{Style.RESET_ALL}")