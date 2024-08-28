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
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        logging.error(f"Error geocoding address: {address}: {e}")
        return None, None

# Directly work with the 'gsa' table
table_name = 'gsa'
logging.info(f"Processing table {table_name}")
check_and_add_columns(table_name)

# Select the 'location' column from the table only if latitude or longitude is NULL
cursor.execute(f"SELECT `location`, latitude, longitude FROM {table_name} WHERE `location` IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
addresses = cursor.fetchall()

previous_address = None
previous_latitude = None
previous_longitude = None

for address, latitude, longitude in addresses:
    # Skip if latitude and longitude are already present
    if latitude is not None and longitude is not None:
        logging.info(f"Skipping address {address} in table {table_name} as latitude and longitude are already present.")
        continue

    # Check if the current address is the same as the previous
    if address == previous_address:
        latitude = previous_latitude
        longitude = previous_longitude
    else:
        latitude, longitude = geocode_address(address)

    previous_address = address
    previous_latitude = latitude
    previous_longitude = longitude

    # Update the database if coordinates obtained
    if latitude is not None and longitude is not None:
        update_query = f"UPDATE {table_name} SET latitude=%s, longitude=%s WHERE `location`=%s"
        cursor.execute(update_query, (latitude, longitude, address))
        connection.commit()
        logging.info(f"Updated {table_name} with Latitude={latitude}, Longitude={longitude} for address {address}")
    else:
        logging.warning(f"Geocoding failed for address {address} in table {table_name}. Latitude and Longitude not updated.")

print("Geocoding and updating completed for 'gsa' table in auctions database.")

cursor.close()
connection.close()
logging.info("Connection to database closed.")
