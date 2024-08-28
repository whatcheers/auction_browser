import pymysql
from geopy.geocoders import Nominatim
import logging
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

# Set up logging to console
logging.basicConfig(level=logging.INFO)

# Connect to the MySQL server
connection = pymysql.connect(
    host='localhost',
    user='whatcheer',
    password='meatwad',
    database='auctions'
)

cursor = connection.cursor()

# Set a custom user agent for geocoding
user_agent = "whatcheer/AI-github"
geolocator = Nominatim(user_agent=user_agent)

# Regex pattern for ZIP code extraction
zip_code_pattern = re.compile(r'\b\d{5}(?:-\d{4})?\b')

def clean_location(raw_location):
    # Basic cleaning to extract usable address
    parts = raw_location.split('\n')
    clean_parts = [part.strip() for part in parts if part.strip() and not part.startswith("[") and not "Pick-up Location" in part]
    cleaned_location = " ".join(clean_parts)
    return cleaned_location

def extract_zip_code_for_fallback(address):
    """
    Extracts the ZIP code from the address for use in the fallback API call.
    """
    matches = zip_code_pattern.findall(address)
    if matches:
        return matches[-1]  # Use the last match, assuming it's the most relevant ZIP code
    return None

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
            logging.info(f"{column} column added to {table_name}.")

def geocode_address(raw_location, cached_locations):
    """
    Attempts to geocode the address, falling back to ZIP code geocoding if necessary.
    Uses a cache of previously geocoded locations to avoid repeated API calls.
    """
    # Extract the address from the raw location data
    match = re.search(r'\[(.*?)\]', raw_location)
    if match:
        address = match.group(1).strip()
    else:
        address = raw_location.strip()

    # Remove any leading/trailing whitespace and newline characters
    address = ' '.join(address.split())

    if address in cached_locations:
        logging.info(f"{Colors.OKBLUE}Using cached location for address: {address}{Colors.ENDC}")
        return cached_locations[address]

    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            latitude, longitude = location.latitude, location.longitude
            cached_locations[address] = (latitude, longitude)
            logging.info(f"{Colors.OKGREEN}Geocoded address: {address}, Latitude: {latitude}, Longitude: {longitude}{Colors.ENDC}")
            return latitude, longitude
        else:
            logging.warning(f"{Colors.WARNING}Geocoding failed for address: {address}{Colors.ENDC}")
    except Exception as e:
        logging.error(f"{Colors.FAIL}Error geocoding original address: {address}: {e}{Colors.ENDC}")

    zip_code = extract_zip_code_for_fallback(address)
    if zip_code:
        try:
            location = geolocator.geocode(zip_code, timeout=10)
            if location:
                latitude, longitude = location.latitude, location.longitude
                cached_locations[address] = (latitude, longitude)
                logging.info(f"{Colors.OKGREEN}Geocoded ZIP code: {zip_code}, Latitude: {latitude}, Longitude: {longitude}{Colors.ENDC}")
                return latitude, longitude
            else:
                logging.warning(f"{Colors.WARNING}Geocoding failed for ZIP code: {zip_code}{Colors.ENDC}")
        except Exception as e:
            logging.error(f"{Colors.FAIL}Error geocoding ZIP code: {zip_code}: {e}{Colors.ENDC}")
    else:
        logging.error(f"{Colors.FAIL}No ZIP code found for fallback geocoding of address: {address}{Colors.ENDC}")
    
    logging.warning(f"{Colors.WARNING}Geocoding failed for address: {address}{Colors.ENDC}")
    return None, None

# Specify the table name directly
table_name = 'publicsurplus'

logging.info(f"Processing table {table_name}")
check_and_add_columns(f"auctions.{table_name}")

# Select the 'location' column from the table only if latitude or longitude is NULL
cursor.execute(f"SELECT `location`, latitude, longitude FROM auctions.{table_name} WHERE `location` IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
addresses = cursor.fetchall()

cached_locations = {}  # Dictionary to store previously geocoded locations

for address_tuple in addresses:
    address = address_tuple[0]
    if address_tuple[1] is not None and address_tuple[2] is not None:
        logging.debug(f"Skipping address {address} as latitude and longitude are already present.")
        continue

    latitude, longitude = geocode_address(address, cached_locations)

    if latitude is not None and longitude is not None:
        update_query = f"UPDATE auctions.{table_name} SET latitude=%s, longitude=%s WHERE `location`=%s"
        cursor.execute(update_query, (latitude, longitude, address))
        connection.commit()
        logging.info(f"Updated Latitude={latitude}, Longitude={longitude} for address {address}")
    else:
        logging.warning(f"Geocoding failed for address {address}. Latitude and Longitude not updated.")

print("Geocoding and updating completed for auctions.publicsurplus table.")

cursor.close()
connection.close()
logging.info("Connection to database closed.")
