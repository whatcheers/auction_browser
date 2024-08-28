import os
import configparser
import mysql.connector

def print_colored(message, color):
    """
    Print a message with the specified color.
    """
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'reset': '\033[0m'
    }
    print(f"{colors[color]}{message}{colors['reset']}")

# Load MySQL connection details from config file
config = configparser.ConfigParser()
config.read('db.cfg')

host = config.get('mysql', 'host')
user = config.get('mysql', 'user')
password = config.get('mysql', 'password')
database = "auctions"

# Create a connection to the MySQL server
try:
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password
    )
except mysql.connector.Error as err:
    print_colored(f"Error connecting to MySQL server: {err}", 'red')
    exit(1)

# Check if the "auctions" database exists
try:
    cursor = conn.cursor()
    cursor.execute(f"SHOW DATABASES LIKE '{database}'")
    result = cursor.fetchone()
    if result:
        print_colored(f"Database '{database}' already exists.", 'yellow')
    else:
        # Create the "auctions" database
        cursor.execute(f"CREATE DATABASE {database}")
        print_colored(f"Database '{database}' created successfully.", 'green')

        # Grant full access to the user
        cursor.execute(f"GRANT ALL PRIVILEGES ON {database}.* TO '{user}'@'{host}'")
        print_colored(f"Full access granted to user '{user}'.", 'green')
except mysql.connector.Error as err:
    print_colored(f"Error checking or creating database: {err}", 'red')
    conn.close()
    exit(1)

# Close the connection
conn.close()