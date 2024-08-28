import json
import mysql.connector
import re
from datetime import datetime
import os
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Configuration for MySQL connection
config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

# Connect to the MySQL database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Check if the 'govdeals' table exists, if not, create it
cursor.execute("SHOW TABLES LIKE 'govdeals'")
table_exists = cursor.fetchone()
if not table_exists:
    create_table = (
        "CREATE TABLE govdeals ("
        "  id INT AUTO_INCREMENT PRIMARY KEY,"
        "  item_name VARCHAR(500),"
        "  location VARCHAR(255),"
        "  current_bid DECIMAL(10,2),"
        "  lot_number VARCHAR(50),"
        "  time_left DATETIME,"
        "  url VARCHAR(255),"
        "  favorite CHAR(1) DEFAULT NULL,"
        "  UNIQUE KEY (lot_number)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
    )
    cursor.execute(create_table)
    print(f"{Fore.GREEN}Table 'govdeals' created successfully.{Style.RESET_ALL}")

# Improved INSERT statement for clarity
add_item = (
    "INSERT INTO govdeals "
    "(item_name, location, current_bid, lot_number, time_left, url) "
    "VALUES (%s, %s, %s, %s, %s, %s) "
    "ON DUPLICATE KEY UPDATE current_bid=VALUES(current_bid)"
)

# Function to convert 'Time Left' to MySQL datetime format
def convert_time_left_to_mysql_datetime(time_left):
    datetime_str = re.search(r'\((.*?)\)', time_left).group(1)
    time_left_obj = datetime.strptime(datetime_str, '%B %d, %Y %I:%M %p %Z')
    return time_left_obj.strftime('%Y-%m-%d %H:%M:%S')

# Get the newest JSON file in the directory
json_files = [f for f in os.listdir('./') if f.endswith('.json')]
newest_file = max(json_files, key=os.path.getctime)

# Load the JSON data from the newest file
with open(newest_file) as json_file:
    items = json.load(json_file)

error_items_count = 0
inserted_items_count = 0

current_timestamp = datetime.now()

# Iterate over the items and insert them into the database
for item in tqdm(items, desc="Inserting items", unit="item"):
    try:
        item_name = item.get('Title', 'Unknown Item')
        location = item.get('Location', 'Unknown Location')
        current_bid = item.get('Current Bid', '0').replace('USD ', '').replace(',', '')
        lot_number = item.get('Lot Number', '0')
        time_left = item.get('Time Left', '')
        url = item.get('URL', 'No URL Provided')

        current_bid_float = float(current_bid)

        # Convert 'Time Left' to MySQL DATETIME format
        time_left_mysql_format = convert_time_left_to_mysql_datetime(time_left)

        data_item = (item_name, location, current_bid_float, lot_number, time_left_mysql_format, url)
        cursor.execute(add_item, data_item)
        inserted_items_count += 1
    except Exception as e:
        error_message = str(e)
        if "1287: 'VALUES function' is deprecated" not in error_message:
            with open('import-errors.txt', 'a') as error_log:
                error_log.write(f"Item: {item_name} - Error: {error_message}\n")
            error_items_count += 1
        pass

# Commit and close connections
cnx.commit()
cursor.close()
cnx.close()

print(f"{Fore.GREEN}{inserted_items_count} items inserted successfully.")
print(f"{Fore.YELLOW}{error_items_count} items encountered errors.{Style.RESET_ALL}")
