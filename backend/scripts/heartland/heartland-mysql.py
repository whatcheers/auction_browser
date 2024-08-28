import json
import mysql.connector

# MySQL database connection parameters
mysql_config = {
    'host': 'localhost',
    'user': 'whatcheer',
    'password': 'meatwad',
    'database': 'auctions'
}

# Function to check if table exists in MySQL database
def table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

# Function to create table in MySQL database
def create_table(cursor):
    cursor.execute("""
        CREATE TABLE auctions.heartland (
            item_name VARCHAR(255),
            location VARCHAR(255),
            current_bid DECIMAL(10,2),
            lot_number VARCHAR(50) PRIMARY KEY,
            time_left DATETIME,
            url VARCHAR(255),
            category VARCHAR(100),  -- Added category field
            latitude FLOAT,
            longitude FLOAT
        )
    """)

# Function to insert data into MySQL database
def insert_data(cursor, data):
    for item in data:
        # Adding default values for latitude and longitude
        item['latitude'] = 41.637900
        item['longitude'] = -91.493070

        # The 'time_left' field is expected to be in the correct format already,
        # so there's no need to parse and reformat it

        cursor.execute("""
            INSERT INTO auctions.heartland 
            (item_name, location, current_bid, lot_number, time_left, url, category, latitude, longitude) 
            VALUES (%(item_name)s, %(location)s, %(current_bid)s, %(lot_number)s, %(time_left)s, %(url)s, %(category)s, %(latitude)s, %(longitude)s)
            ON DUPLICATE KEY UPDATE
            item_name = VALUES(item_name),
            location = VALUES(location),
            current_bid = VALUES(current_bid),
            time_left = VALUES(time_left),
            url = VALUES(url),
            category = VALUES(category),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude)
        """, item)

# Main function
def main():
    # Connect to MySQL database
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # Check if table exists, if not, create it
        if not table_exists(cursor, 'heartland'):
            create_table(cursor)
            print("Table 'auctions.heartland' created successfully.")

        # Open JSON file and insert data into database
        with open('heartland-import.json', 'r') as file:
            data = json.load(file)
            insert_data(cursor, data)
            conn.commit()
            print("Data inserted successfully.")

    except mysql.connector.Error as error:
        print(f"Error: {error}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    main()
