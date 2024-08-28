import pymysql
from geopy.geocoders import Nominatim
import logging
import re
from tqdm import tqdm
from colorama import init, Fore, Style

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("geocoding.log"),
                        logging.StreamHandler()
                    ])

# Database connection setup
connection = pymysql.connect(
    host='localhost',
    user='whatcheer',
    password='meatwad',
    database='auctions'
)
cursor = connection.cursor()

# Set up geolocator with a custom user agent
user_agent = "whatcheers/AI-github"
geolocator = Nominatim(user_agent=user_agent)

# Caches
geocode_cache = {}  # Cache to store geocoding results to avoid duplicate requests
location_cache = {}  # Cache to avoid API calls for locations with known lat-long

def check_and_add_columns(table_name):
    columns_to_add = ['latitude', 'longitude']
    for column in columns_to_add:
        cursor.execute(f"SHOW COLUMNS FROM `auctions`.`{table_name}` LIKE '{column}'")
        result = cursor.fetchone()
        if not result:
            cursor.execute(f"ALTER TABLE `auctions`.`{table_name}` ADD COLUMN `{column}` FLOAT")
            logging.info(f"{Fore.GREEN}Added column {column} to table `auctions`.`{table_name}`.{Style.RESET_ALL}")

def extract_zip_code(address):
    match = re.search(r'\b\d{5}\b', address)
    return match.group(0) if match else None

def geocode_address(address):
    if address in geocode_cache:
        return geocode_cache[address]
    # Check if we've already geocoded a different address to the same location
    for cached_address, (lat, lon) in geocode_cache.items():
        if lat is not None and lon is not None and location_cache.get((lat, lon)) == address:
            return lat, lon
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            geocode_cache[address] = (location.latitude, location.longitude)
            location_cache[(location.latitude, location.longitude)] = address
            return location.latitude, location.longitude
        else:
            zip_code = extract_zip_code(address)
            if zip_code:
                if zip_code in geocode_cache:
                    return geocode_cache[zip_code]
                location = geolocator.geocode(zip_code, timeout=10)
                if location:
                    geocode_cache[zip_code] = (location.latitude, location.longitude)
                    location_cache[(location.latitude, location.longitude)] = address
                    return location.latitude, location.longitude
            geocode_cache[address] = (None, None)
            return None, None
    except Exception as e:
        logging.error(f"{Fore.RED}Geocode exception: {e}{Style.RESET_ALL}")
        geocode_cache[address] = (None, None)
        return None, None

cursor.execute("SHOW TABLES LIKE 'hibid';")
tables = cursor.fetchall()

total_addresses = 0
updated_addresses = 0
skipped_addresses = 0

for table in tables:
    table_name = table[0]
    check_and_add_columns(table_name)
    
    cursor.execute(f"SELECT location, latitude, longitude FROM `auctions`.`hibid` WHERE location IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
    addresses = cursor.fetchall()
    total_addresses += len(addresses)

with tqdm(total=total_addresses, desc="Geocoding progress", unit="address", ncols=100) as pbar:
    for table in tables:
        table_name = table[0]
        
        cursor.execute(f"SELECT location, latitude, longitude FROM `auctions`.`hibid` WHERE location IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
        addresses = cursor.fetchall()
        
        for address, _, _ in addresses:
            geocoded_lat, geocoded_lon = geocode_address(address)
            if geocoded_lat and geocoded_lon:
                update_query = f"UPDATE `auctions`.`hibid` SET latitude=%s, longitude=%s WHERE location=%s"
                cursor.execute(update_query, (geocoded_lat, geocoded_lon, address))
                connection.commit()
                updated_addresses += 1
            else:
                skipped_addresses += 1
            pbar.update(1)

logging.info(f"{Fore.GREEN}Geocoding process completed.{Style.RESET_ALL}")
logging.info(f"{Fore.BLUE}Total addresses: {total_addresses}{Style.RESET_ALL}")
logging.info(f"{Fore.GREEN}Updated addresses: {updated_addresses}{Style.RESET_ALL}")
logging.info(f"{Fore.YELLOW}Skipped addresses: {skipped_addresses}{Style.RESET_ALL}")

cursor.close()
connection.close()