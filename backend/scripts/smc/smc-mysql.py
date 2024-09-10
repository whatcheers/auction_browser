import json
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from colorama import Fore, Style
from tqdm import tqdm

# Database configuration details
db_config = {
    "user": "whatcheer",
    "password": "meatwad",
    "host": "localhost",
    "database": "auctions",
    "raise_on_warnings": True
}

# Initialize statistics
stats = {
    "items_added": 0,
    "items_updated": 0,
    "items_skipped": 0,
    "items_removed": 0,
    "errors": 0
}

def update_statistics():
    try:
        with open('smc_statistics.json', 'r') as f:
            existing_stats = json.load(f)
        for key in stats:
            existing_stats[key] = (existing_stats.get(key, 0) or 0) + stats[key]
        with open('smc_statistics.json', 'w') as f:
            json.dump(existing_stats, f, indent=2)
    except FileNotFoundError:
        with open('smc_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)

def connect_to_database(config):
    print("Attempting to connect to the database...")
    try:
        cnx = mysql.connector.connect(**config)
        print(f"{Fore.GREEN}Successfully connected to the database.{Style.RESET_ALL}")
        return cnx
    except mysql.connector.Error as err:
        print(f"{Fore.RED}Database connection failed: {err}{Style.RESET_ALL}")
        stats["errors"] += 1
    return None

def ensure_table_exists(cnx):
    print("Ensuring the 'smc' table exists...")
    cursor = cnx.cursor()
    table_check_query = "SHOW TABLES LIKE 'smc'"
    cursor.execute(table_check_query)
    result = cursor.fetchone()
    if not result:
        print("Table 'smc' does not exist. Creating the table...")
        create_table_query = """
        CREATE TABLE smc (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(255) NULL,
            location VARCHAR(255) NULL,
            current_bid DECIMAL(10,2) NULL,
            lot_number VARCHAR(50) NULL,
            time_left DATETIME NULL,
            url VARCHAR(500) NULL,
            latitude DECIMAL(11,8) NULL,
            longitude DECIMAL(12,8) NULL,
            favorite CHAR(1) NULL
        )
        """
        cursor.execute(create_table_query)
        print(f"{Fore.GREEN}Table 'smc' created successfully.{Style.RESET_ALL}")
    else:
        print("Table 'smc' already exists.")
    cursor.close()

def clean_up_expired_auctions(cnx):
    print("Cleaning up expired auctions...")
    cursor = cnx.cursor()
    delete_query = "DELETE FROM smc WHERE time_left < %s"
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Current datetime for deletion: {current_datetime}")
    try:
        cursor.execute(delete_query, (current_datetime,))
        stats["items_removed"] = cursor.rowcount
        print(f"{Fore.GREEN}Deleted {cursor.rowcount} expired auctions.{Style.RESET_ALL}")
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"{Fore.RED}Error cleaning up expired auctions: {err}{Style.RESET_ALL}")
        stats["errors"] += 1
    finally:
        cursor.close()

def insert_data(cnx, data):
    print("Updating table...")
    cursor = cnx.cursor()
    insert_query = """
    INSERT INTO smc (item_name, location, current_bid, lot_number, time_left, url, latitude, longitude, favorite)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) AS new_values
    ON DUPLICATE KEY UPDATE
        item_name = new_values.item_name,
        location = new_values.location,
        current_bid = new_values.current_bid,
        time_left = new_values.time_left,
        url = new_values.url,
        latitude = new_values.latitude,
        longitude = new_values.longitude,
        favorite = new_values.favorite
    """
    progress_bar = tqdm(total=len(data), unit='item', desc='Progress')
    for item in data:
        time_left = item.get('time_left', None)
        if time_left:
            try:
                # Convert time_left from ISO 8601 to MySQL datetime format
                time_left = datetime.fromisoformat(time_left.replace('Z', '')).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                print(f"{Fore.YELLOW}Invalid datetime format for time_left: {time_left}. Setting to NULL.{Style.RESET_ALL}")
                time_left = None

        values = (
            item.get('item_name', None),
            item.get('location', None),
            float(item.get('current_bid', 0.0).replace(',', '')),
            item.get('lot_number', None),
            time_left,
            item.get('url', None),
            item.get('latitude', None),
            item.get('longitude', None),
            item.get('favorite', None)
        )
        try:
            cursor.execute(insert_query, values)
            if cursor.rowcount > 0:
                if cursor.lastrowid:
                    stats["items_added"] += 1
                else:
                    stats["items_updated"] += 1
            else:
                stats["items_skipped"] += 1
        except mysql.connector.Error as err:
            print(f"{Fore.RED}Failed to insert or update item {item.get('item_name', '')}: {err}{Style.RESET_ALL}")
            stats["errors"] += 1
        progress_bar.update(1)
    progress_bar.close()
    cnx.commit()
    cursor.close()

if __name__ == "__main__":
    print("Script execution started.")
    json_file_path = 'auction_data.json'  # Ensure this is the correct path to your JSON file
    try:
        with open(json_file_path, 'r') as file:
            all_items = json.load(file)  # Load JSON data directly into a list

        cnx = connect_to_database(db_config)
        if cnx:
            ensure_table_exists(cnx)  # Check and create the table if it doesn't exist
            clean_up_expired_auctions(cnx)  # Clean up expired auctions
            insert_data(cnx, all_items)  # Pass the list of items directly to the insert function
            cnx.close()
        else:
            print(f"{Fore.RED}Failed to connect to the database.{Style.RESET_ALL}")
            stats["errors"] += 1
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        stats["errors"] += 1

    # Save statistics
    update_statistics()

    print(f"\n{Fore.BLUE}SMC MySQL Statistics:{Style.RESET_ALL}")
    print(f"Items added: {stats['items_added']}")
    print(f"Items updated: {stats['items_updated']}")
    print(f"Items skipped: {stats['items_skipped']}")
    print(f"Items removed: {stats['items_removed']}")
    print(f"Errors: {stats['errors']}")