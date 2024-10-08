import pymysql
from geopy.geocoders import Nominatim
import logging
from colorama import init, Fore, Style
from tqdm import tqdm
import json

# Initialize colorama
init()

# Set up logging to console with colors
logging.basicConfig(level=logging.INFO, format=f"{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - {Fore.BLUE}%(levelname)s{Style.RESET_ALL} - %(message)s")

# Connect to the MySQL server
connection = pymysql.connect(
    host='localhost',
    user='whatcheer',
    password='meatwad',
    database='auctions'
)

cursor = connection.cursor()

# Set a custom user agent for geocoding
user_agent = "whatcheers/AI-github"
geolocator = Nominatim(user_agent=user_agent)

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
        with open('smc_statistics.json', 'r') as f:
            existing_stats = json.load(f)
        for key in stats:
            existing_stats[key] = (existing_stats.get(key, 0) or 0) + stats[key]
        with open('smc_statistics.json', 'w') as f:
            json.dump(existing_stats, f, indent=2)
    except FileNotFoundError:
        with open('smc_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)

# Function to check and add latitude, longitude columns if necessary
def check_and_add_columns(table_name):
    columns_to_add = ['latitude', 'longitude']
    for column in columns_to_add:
        check_column_query = f"SHOW COLUMNS FROM {table_name} LIKE '{column}'"
        cursor.execute(check_column_query)
        result = cursor.fetchone()
        if not result:
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN `{column}` FLOAT"
            cursor.execute(alter_query)
            logging.info(f"{Fore.GREEN}Column '{column}' added to table '{table_name}'.{Style.RESET_ALL}")

def geocode_address(address):
    default_latitude = 44.5
    default_longitude = -89.5

    # Return default coordinates if the address is empty
    if not address:
        logging.warning(f"{Fore.YELLOW}Empty address encountered. Using default coordinates.{Style.RESET_ALL}")
        stats["addresses_skipped"] += 1
        return default_latitude, default_longitude

    # Existing geocoding logic...
    parts = [part.strip() for part in address.split(',')]
    fallbacks = [address]  # Start with the full address

    if len(parts) > 1:
        city_state = ', '.join(parts[-2:])  # Combine the last two parts (usually city and state)
        fallbacks.append(city_state)

    fallbacks.append(parts[0])

    for attempt in fallbacks:
        try:
            location = geolocator.geocode(attempt, timeout=10)
            if location:
                latitude = location.latitude
                longitude = location.longitude
                if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                    return latitude, longitude
        except Exception as e:
            logging.error(f"{Fore.RED}Geocoding attempt failed for address '{attempt}': {e}{Style.RESET_ALL}")
            stats["errors"] += 1

    logging.warning(f"{Fore.YELLOW}All geocoding attempts failed for address: '{address}'. Using default coordinates.{Style.RESET_ALL}")
    stats["addresses_skipped"] += 1
    return default_latitude, default_longitude

# Process only the 'smc' table
table_name = 'smc'
logging.info(f"{Fore.MAGENTA}Processing table '{table_name}'{Style.RESET_ALL}")
check_and_add_columns(table_name)

# Select the 'location' column from the table only if latitude or longitude is NULL
cursor.execute(f"SELECT `location` FROM {table_name} WHERE `location` IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
addresses = cursor.fetchall()

total_addresses = len(addresses)
logging.info(f"{Fore.BLUE}Total addresses to process: {total_addresses}{Style.RESET_ALL}")

# Create a progress bar
progress_bar = tqdm(total=total_addresses, unit='address', desc='Geocoding Progress')

for address, in addresses:
    latitude, longitude = geocode_address(address)
    
    update_query = f"UPDATE {table_name} SET latitude=%s, longitude=%s WHERE `location`=%s"
    cursor.execute(update_query, (latitude, longitude, address))
    connection.commit()

    stats["addresses_processed"] += 1
    stats["addresses_updated"] += 1

    # Update the progress bar
    progress_bar.update(1)

# Close the progress bar
progress_bar.close()

logging.info(f"{Fore.GREEN}Geocoding and updating completed for table '{table_name}' in 'auctions' database.{Style.RESET_ALL}")

cursor.close()
connection.close()
logging.info(f"{Fore.MAGENTA}Connection to database closed.{Style.RESET_ALL}")

# Save statistics
update_statistics()

logging.info(f"{Fore.BLUE}Summary:{Style.RESET_ALL}")
logging.info(f"{Fore.CYAN}Total addresses processed: {stats['addresses_processed']}{Style.RESET_ALL}")
logging.info(f"{Fore.CYAN}Addresses updated: {stats['addresses_updated']}{Style.RESET_ALL}")
logging.info(f"{Fore.CYAN}Addresses skipped: {stats['addresses_skipped']}{Style.RESET_ALL}")
logging.info(f"{Fore.CYAN}Errors encountered: {stats['errors']}{Style.RESET_ALL}")