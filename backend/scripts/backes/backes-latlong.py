import pymysql
from geopy.geocoders import Nominatim
import logging

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
user_agent = "whatcheers/AI-github"
geolocator = Nominatim(user_agent=user_agent)

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
            logging.info(f"{column} column added to {table_name}.")

# Function to geocode using different methods
def geocode_address(address):
    # Preset default coordinates for the center of Wisconsin
    default_latitude = 44.5
    default_longitude = -89.5

    address_parts = address.split(',')
    fallbacks = [address]

    # Adjust the fallback logic based on the parts of the address available
    if len(address_parts) >= 3:
        # Full address available
        fallbacks += [f"{address_parts[-3]}, {address_parts[-2]}", address_parts[-1].strip().split(' ')[-1]]
    elif len(address_parts) == 2:
        # Only city and state available
        fallbacks += [address_parts[1].strip().split(' ')[-1]]
    elif len(address_parts) == 1:
        # Only zip code or city available
        pass  # No further fallback needed

    for attempt in fallbacks:
        try:
            location = geolocator.geocode(attempt, timeout=10)
            if location:
                return location.latitude, location.longitude
        except Exception as e:
            logging.error(f"Attempt for geocoding address '{attempt}' failed: {e}")
    
    # If all attempts fail, log a warning and return default coordinates
    logging.warning(f"All geocoding attempts failed for address: '{address}'. Using default coordinates.")
    return default_latitude, default_longitude

# Define table name directly
table_name = "backes"

# Processing the specific table
logging.info(f"Processing table {table_name}")
check_and_add_columns(table_name)

# Select the 'location' column from the table only if latitude or longitude is NULL
cursor.execute(f"SELECT `location`, latitude, longitude FROM {table_name} WHERE `location` IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
addresses = cursor.fetchall()

previous_address = None
previous_latitude = None
previous_longitude = None

for address, latitude, longitude in addresses:
    # Check if latitude and longitude are already present
    if latitude is not None and longitude is not None:
        logging.info(f"Skipping address {address} in table {table_name} as latitude and longitude are already present.")
        continue

    # Check if the current address is the same as the previous address
    if address == previous_address:
        # If so, copy the latitude and longitude from the previous record
        latitude = previous_latitude
        longitude = previous_longitude
    else:
        # Otherwise, attempt to geocode the address
        latitude, longitude = geocode_address(address)

    # Update the previous address and coordinates for the next iteration
    previous_address = address
    previous_latitude = latitude
    previous_longitude = longitude

    # Update the database if latitude and longitude are obtained
    if latitude is not None and longitude is not None:
        update_query = f"UPDATE {table_name} SET latitude=%s, longitude=%s WHERE `location`=%s"
        cursor.execute(update_query, (latitude, longitude, address))
        connection.commit()
        logging.info(f"Updated {table_name} with Latitude={latitude}, Longitude={longitude} for address {address}")
    else:
        logging.warning(f"Geocoding failed for address {address} in table {table_name}. Latitude and Longitude not updated.")

print("Geocoding and updating completed for table backes.")

cursor.close()
connection.close()
logging.info("Connection to database closed.")
