import mysql.connector
from termcolor import colored
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
    deleted_records_count = cursor.rowcount
    print(colored(f"{deleted_records_count} expired records have been deleted from the govdeals table.", "green"))

    # Commit the changes to the database
    cnx.commit()

except mysql.connector.Error as err:
    logging.error(f"Error: '{err}'")
    print(colored("An error occurred. Check the error log for more details.", "red"))
finally:
    # Close the cursor and connection
    if 'cursor' in locals():
        cursor.close()
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
