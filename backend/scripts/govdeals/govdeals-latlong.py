import pymysql
from geopy.geocoders import Nominatim
import time
import logging
from colorama import init, Fore, Style

# Initialize colorama
init()

# Set up logging to track geocoding process and errors
logging.basicConfig(filename='geocoding.log', level=logging.INFO)

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'whatcheer',
    'password': 'meatwad',
    'database': 'auctions'
}

def establish_db_connection(config):
    print(f"{Fore.GREEN}Connecting to the MySQL server...{Style.RESET_ALL}")
    connection = pymysql.connect(**config)
    print(f"{Fore.GREEN}Connection established.{Style.RESET_ALL}")
    return connection

def check_and_add_columns(cursor, table_name, columns):
    for column in columns:
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column}'")
        column_exists = cursor.fetchone()
        if not column_exists:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} DECIMAL(10,8)")
            print(f"{Fore.GREEN}Added '{column}' column to the '{table_name}' table.{Style.RESET_ALL}")

# Establish connection to the MySQL database
connection = establish_db_connection(db_config)

# Prepare for database operations
cursor = connection.cursor()

# Check if the 'latitude' and 'longitude' columns exist in the 'govdeals' table
check_and_add_columns(cursor, 'govdeals', ['latitude', 'longitude'])

# Nominatim user-agent setup
user_agent = "whatcheers/AI-github"
geolocator = Nominatim(user_agent=user_agent)

# Fetch unique locations where geocoding is needed
select_query = """
SELECT DISTINCT location
FROM govdeals
WHERE (latitude IS NULL OR longitude IS NULL) AND location != ''
"""
cursor.execute(select_query)
locations = cursor.fetchall()
print(f"{Fore.GREEN}Fetched {len(locations)} unique locations needing geocoding.{Style.RESET_ALL}")

# Cache for geocoding results
location_cache = {}

def geocode_and_update_db(locations, geolocator, cursor, connection, location_cache):
    # Geocode unique locations and update the database
    for location in locations:
        location = location[0]
        if location not in location_cache:
            try:
                geocoded_location = geolocator.geocode(location, timeout=10)
                if geocoded_location:
                    latitude, longitude = geocoded_location.latitude, geocoded_location.longitude
                    # Check if the latitude and longitude values are within the valid range
                    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                        location_cache[location] = (latitude, longitude)
                        print(f"{Fore.GREEN}Geocoded {location}: Latitude={latitude}, Longitude={longitude}{Style.RESET_ALL}")
                        # Update all rows with this location
                        update_query = "UPDATE govdeals SET latitude=%s, longitude=%s WHERE location=%s"
                        cursor.execute(update_query, (latitude, longitude, location))
                        connection.commit()
                        print(f"{Fore.GREEN}Updated rows with location '{location}' in the database.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Invalid geocode result for {location}: Latitude={latitude}, Longitude={longitude}{Style.RESET_ALL}")
                        logging.warning(f"Invalid geocode result for {location}: Latitude={latitude}, Longitude={longitude}")
                    time.sleep(1)  # Respect API usage policy
                else:
                    print(f"{Fore.YELLOW}No geocode result for {location}{Style.RESET_ALL}")
                    logging.warning(f"No geocode result for {location}")
                    continue
            except Exception as e:
                print(f"{Fore.RED}Error geocoding {location}: {e}{Style.RESET_ALL}")
                logging.error(f"Error geocoding {location}: {e}")
                continue

# Cleanup
def cleanup(cursor, connection):
    cursor.close()
    connection.close()
    print(f"{Fore.GREEN}Database connection closed.{Style.RESET_ALL}")

# Call the function with the necessary parameters
geocode_and_update_db(locations, geolocator, cursor, connection, location_cache)
cleanup(cursor, connection)