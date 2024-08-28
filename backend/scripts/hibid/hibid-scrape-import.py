import json
import mysql.connector
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from colorama import Fore, Style
import glob
import subprocess

def convert_time_left(time_left):
    if time_left is None or time_left == 'N/A':
        return None
    if '.' in time_left:
        time_left = time_left.split('.')[0]
    return time_left

def handle_bid_price(price):
    return float(price) if price != 'N/A' else 0.00

config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

script_dir = os.path.dirname(os.path.abspath(__file__))

create_table = """
CREATE TABLE IF NOT EXISTS auctions.hibid (
  id INT AUTO_INCREMENT PRIMARY KEY,
  lot_number VARCHAR(255) NOT NULL,
  number_of_bids VARCHAR(255) NULL,
  time_left DATETIME NULL,
  url VARCHAR(255) UNIQUE,
  item_name VARCHAR(255) NULL,
  current_bid_price DECIMAL(10,2) NULL,
  location_link VARCHAR(255) NULL,
  location VARCHAR(255) NULL,
  favorite CHAR(1) DEFAULT 'N',
  latitude DECIMAL(11,8) NULL,
  longitude DECIMAL(12,8) NULL
);
"""

add_item = """
    INSERT INTO auctions.hibid
    (lot_number, number_of_bids, time_left, url, item_name, current_bid_price, location_link, location, favorite, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'N', NULL, NULL)
    AS new
    ON DUPLICATE KEY UPDATE
    number_of_bids = new.number_of_bids,
    time_left = new.time_left,
    item_name = new.item_name,
    current_bid_price = new.current_bid_price,
    location_link = new.location_link,
    location = new.location
"""

successful_items = 0
duplicate_items = 0
skipped_items = []

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
except mysql.connector.Error as err:
    print(f"{Fore.RED}Error connecting to the database: {err}{Style.RESET_ALL}")
    exit(1)

auction_url = "https://hibid.com/catalog/562468/online-only-jewelry-auction"

try:
    cursor.execute("SHOW TABLES IN auctions LIKE 'hibid'")
    if not cursor.fetchone():
        cursor.execute(create_table)
        print(f"{Fore.GREEN}Table 'auctions.hibid' created.{Style.RESET_ALL}")
except mysql.connector.Error as err:
    print(f"{Fore.RED}Error checking or creating the 'auctions.hibid' table: {err}{Style.RESET_ALL}")
    cursor.close()
    cnx.close()
    exit(1)

json_files = glob.glob(os.path.join(script_dir, 'scrape-*_parsed.json'))
if json_files:
    latest_file = max(json_files, key=os.path.getctime)
    with open(latest_file) as json_file:
        items = json.load(json_file)

        for item in items:
            try:
                lot_number = item.get('lot_number')
                item_name = item.get('item_name')
                location = item.get('location')
                url = item.get('url')
                number_of_bids = item.get('number_of_bids', 'N/A')
                time_left = convert_time_left(item.get('time_left', 'N/A'))
                current_bid_price = handle_bid_price(item.get('current_bid_price', 'N/A'))
                location_link = item.get('location_link')

                data_item = (lot_number, number_of_bids, time_left, url, item_name, current_bid_price, location_link, location)
                cursor.execute(add_item, data_item)
                successful_items += 1
            except mysql.connector.Error as err:
                print(f"{Fore.RED}Error inserting item: {item}. Error: {err}{Style.RESET_ALL}")
                skipped_items.append(item)
            except Exception as e:
                print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
                skipped_items.append(item)

        cnx.commit()

cursor.close()
cnx.close()

print(f"{Fore.GREEN}Successful insertions: {successful_items}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Duplicate items: {duplicate_items}{Style.RESET_ALL}")
print(f"{Fore.RED}Skipped items: {len(skipped_items)}{Style.RESET_ALL}")

try:
    subprocess.run(["python3", "hibid-latlong.py"], check=True)
    print(f"{Fore.GREEN}hibid-latlong.py script executed successfully.{Style.RESET_ALL}")
except FileNotFoundError:
    print(f"{Fore.RED}hibid-latlong.py script not found. Please check the file path.{Style.RESET_ALL}")
except subprocess.CalledProcessError as e:
    print(f"{Fore.RED}Error occurred while running hibid-latlong.py: {e}{Style.RESET_ALL}")
