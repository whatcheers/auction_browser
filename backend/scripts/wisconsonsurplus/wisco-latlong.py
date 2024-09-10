import mysql.connector
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import json
from colorama import init, Fore, Style
import logging

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Database connection details
db_config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
}

def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            logging.info(f"{Fore.GREEN}Successfully connected to the database.{Style.RESET_ALL}")
            return connection
    except mysql.connector.Error as e:
        logging.error(f"{Fore.RED}Error connecting to the database: {e}{Style.RESET_ALL}")
        stats["errors"] += 1
    return None

def geocode_address(geolocator, address):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                logging.warning(f"{Fore.YELLOW}No location found for address: {address}{Style.RESET_ALL}")
                stats["addresses_skipped"] += 1
                return None, None
        except (GeocoderTimedOut, GeocoderServiceError):
            if attempt < max_attempts - 1:
                time.sleep(1)
            else:
                logging.error(f"{Fore.RED}Geocoding failed after {max_attempts} attempts for address: {address}{Style.RESET_ALL}")
                stats["errors"] += 1
                return None, None

def update_coordinates():
    connection = connect_to_database()
    if not connection:
        return

    try:
        cursor = connection.cursor()
        geolocator = Nominatim(user_agent="wisco_surplus_geocoder")

        # Fetch rows with missing coordinates
        cursor.execute("SELECT id, location FROM wiscosurp_auctions WHERE latitude IS NULL OR longitude IS NULL")
        rows = cursor.fetchall()

        for row in rows:
            id, address = row
            stats["addresses_processed"] += 1
            
            if not address:
                logging.warning(f"{Fore.YELLOW}Skipping empty address for id {id}{Style.RESET_ALL}")
                stats["addresses_skipped"] += 1
                continue

            latitude, longitude = geocode_address(geolocator, address)
            
            if latitude is not None and longitude is not None:
                update_query = "UPDATE wiscosurp_auctions SET latitude = %s, longitude = %s WHERE id = %s"
                cursor.execute(update_query, (latitude, longitude, id))
                connection.commit()
                stats["addresses_updated"] += 1
                logging.info(f"{Fore.GREEN}Updated coordinates for id {id}: {latitude}, {longitude}{Style.RESET_ALL}")
            else:
                logging.warning(f"{Fore.YELLOW}Could not geocode address for id {id}: {address}{Style.RESET_ALL}")
                stats["addresses_skipped"] += 1

            # Add a small delay to avoid overwhelming the geocoding service
            time.sleep(1)

    except mysql.connector.Error as e:
        logging.error(f"{Fore.RED}Database error: {e}{Style.RESET_ALL}")
        stats["errors"] += 1
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            logging.info(f"{Fore.GREEN}Database connection closed.{Style.RESET_ALL}")

def main():
    update_coordinates()

    # Save statistics
    update_statistics()

    logging.info(f"{Fore.BLUE}Wisconsin Surplus Lat/Long Statistics:{Style.RESET_ALL}")
    logging.info(f"Addresses processed: {stats['addresses_processed']}")
    logging.info(f"Addresses updated: {stats['addresses_updated']}")
    logging.info(f"Addresses skipped: {stats['addresses_skipped']}")
    logging.info(f"Errors: {stats['errors']}")

if __name__ == "__main__":
    main()