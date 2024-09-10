import mysql.connector
from termcolor import colored
import json
import logging

# Setup logger for error logging
log_filename = "error_log.txt"
logging.basicConfig(filename=log_filename, level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Configuration for MySQL connection
config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

try:
    # Connect to the MySQL database
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # Delete expired records from the govdeals table
    delete_expired_records = """
    DELETE FROM govdeals 
    WHERE time_left < NOW();
    """
    cursor.execute(delete_expired_records)

    # Get the count of deleted records
    items_removed = cursor.rowcount
    print(colored(f"{items_removed} expired records have been deleted from the govdeals table.", "green"))

    # Update statistics
    try:
        with open('../govdeals_statistics.json', 'r+') as f:
            stats = json.load(f)
            stats['items_removed'] = items_removed
            f.seek(0)
            json.dump(stats, f)
            f.truncate()
    except FileNotFoundError:
        with open('../govdeals_statistics.json', 'w') as f:
            json.dump({'items_removed': items_removed}, f)

except mysql.connector.Error as err:
    logging.error(f"Error: '{err}'")
    print(colored("An error occurred. Check the error log for more details.", "red"))
finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
