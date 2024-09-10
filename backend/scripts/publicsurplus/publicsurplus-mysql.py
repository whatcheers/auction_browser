import json
import mysql.connector
import os
from datetime import datetime
import re

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

# Connect to the database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor(buffered=True)  # Use a buffered cursor

def clean_location(raw_location):
    # Basic cleaning to extract usable address
    parts = raw_location.split('\n')
    clean_parts = [part.strip() for part in parts if part.strip() and not part.startswith("[") and not "Pick-up Location" in part]
    cleaned_location = " ".join(clean_parts)
    return cleaned_location

def check_and_add_columns(table_name):
    """
    Checks for the presence of latitude and longitude columns in the table,
    and adds them if they are missing.
    """
    columns_to_add = ['latitude', 'longitude']
    for column in columns_to_add:
        check_column_query = f"SHOW COLUMNS FROM {table_name} LIKE '{column}'"
        cursor.execute(check_column_query)
        result = cursor.fetchone()
        if not result:
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN `{column}` FLOAT"
            cursor.execute(alter_query)
            print(f"{Colors.OKGREEN}{column} column added to {table_name}.{Colors.ENDC}")

def check_and_remove_expired_rows(table_name):
    """
    Checks for expired rows in the table and removes them.
    """
    try:
        # Convert time_left field to date type if needed
        cursor.execute(f"ALTER TABLE {table_name} MODIFY time_left DATE")
        cnx.commit()

        # Delete expired records directly
        cursor.execute(f"DELETE FROM {table_name} WHERE time_left < CURDATE()")
        deleted_rows = cursor.rowcount  # Get the number of deleted rows
        cnx.commit()

        if deleted_rows > 0:
            print(f"{Colors.WARNING}{deleted_rows} expired records have been deleted from {table_name}.{Colors.ENDC}")
        else:
            print(f"{Colors.OKBLUE}No expired records found in {table_name}.{Colors.ENDC}")
    except mysql.connector.Error as err:
        print(f"{Colors.FAIL}An error occurred while checking/removing expired rows: {err}{Colors.ENDC}")
        cnx.rollback()

# Ensure the 'publicsurplus' table exists
try:
    cursor.execute("SELECT 1 FROM publicsurplus LIMIT 1")
    cursor.fetchall()  # Fetch all results to clear them
except mysql.connector.Error as err:
    if err.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:
        print(f"{Colors.OKBLUE}Table 'publicsurplus' does not exist. Creating it...{Colors.ENDC}")
        cursor.execute("""
            CREATE TABLE publicsurplus (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(255) NULL,
                location VARCHAR(255) NULL,
                current_bid DECIMAL(10,2) NULL,
                lot_number INT UNIQUE NULL,
                time_left DATETIME NULL,
                url VARCHAR(255) NULL,
                favorite CHAR(1) NULL,
                latitude DECIMAL(11,8) NULL,
                longitude DECIMAL(12,8) NULL
            )
        """)
        cursor.execute("ALTER TABLE publicsurplus MODIFY COLUMN time_left DATETIME")
        print(f"{Colors.OKGREEN}Table 'publicsurplus' created successfully.{Colors.ENDC}")
        check_and_add_columns("publicsurplus")
    else:
        print(f"{Colors.FAIL}Error checking for the 'publicsurplus' table: {err}{Colors.ENDC}")
        cursor.close()
        cnx.close()
        exit(1)

# Check and remove expired rows from the 'publicsurplus' table
check_and_remove_expired_rows("publicsurplus")

# Load items from JSON
json_files = [f for f in os.listdir('./archive/') if f.endswith('.json')]
if json_files:
    newest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join('./archive/', f)))
    with open(os.path.join('./archive/', newest_file)) as json_file:
        items = json.load(json_file)
else:
    print(f"{Colors.WARNING}No JSON files found in the './archive/' directory.{Colors.ENDC}")
    items = []  # Set items to an empty list if no JSON files are found

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

# Process items
total_records = len(items)
for item in items:
    try:
        item['location'] = clean_location(item['location'])
        cursor.execute("SELECT COUNT(*) FROM publicsurplus WHERE lot_number = %s", (item['lot_number'],))
        count = cursor.fetchone()[0]
        if count > 0:
            stats["items_skipped"] += 1
            print(f"{Colors.WARNING}Skipped duplicate item with lot_number: {item['lot_number']}{Colors.ENDC}")
            continue

        time_left = datetime.strptime(item['time_left'], '%m/%d/%Y %H:%M')
        cursor.execute("INSERT INTO publicsurplus (item_name, location, current_bid, lot_number, time_left, url, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (item['item_name'], item['location'], item['current_bid'], item['lot_number'], time_left, item['url'], item.get('latitude', None), item.get('longitude', None)))
        stats["items_added"] += 1
        print(f"{Colors.OKGREEN}Processed item: {item['item_name']} with ID: {cursor.lastrowid}{Colors.ENDC}")
    except KeyError as e:
        stats["errors"] += 1
        print(f"{Colors.FAIL}Skipped item due to missing key: {e.args[0]}{Colors.ENDC}")
    except Exception as e:
        stats["errors"] += 1
        print(f"{Colors.FAIL}Error processing item with ID: {item.get('id', 'Unknown')}. Error: {e}{Colors.ENDC}")

cnx.commit()
cursor.close()
cnx.close()

# Save statistics
with open('publicsurplus_mysql_statistics.json', 'w') as f:
    json.dump(stats, f)

print(f"{Colors.HEADER}Import Summary:{Colors.ENDC}")
print(f"Total Records: {total_records}")
print(f"Records Imported: {stats['items_added']}")
print(f"Records Skipped: {stats['items_skipped']}")
print(f"Records Errored: {stats['errors']}")