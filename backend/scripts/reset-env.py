import os
import fnmatch
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# MySQL credentials
mysql_host = "localhost"
mysql_user = "root"
mysql_password = "meatwad"
mysql_database = "auctions"

# Directory to clean
base_dir = os.path.expanduser("~/AI/scripts/")
log_file_path = os.path.join(base_dir, 'cleanup_log.txt')

# Patterns of files to delete
patterns = [
    'auction-detail.json',
    '*.txt',
    '*.html',
    '*.log',
    'auction_data.json',
    'auctionDetails.json',
    '*.zip',
    '*.tar',
    '*.tar.gz',
    '*.tgz'
]

# Create a log entry
def log_deletion(file_path):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Deleted {file_path}\n")

# Delete matching files in a given directory
def delete_files_in_directory(directory, patterns):
    for root, _, files in os.walk(directory):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                    log_deletion(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

# Drop the MySQL database
def drop_mysql_database(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {database}")
            cursor.close()
            connection.close()
            with open(log_file_path, 'a') as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Dropped database {database}\n")
            print(f"Database '{database}' dropped successfully.")
    except Error as e:
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error dropping database {database}: {e}\n")
        print(f"Error dropping database {database}: {e}")

# Create or clear the log file
with open(log_file_path, 'w') as log_file:
    log_file.write("Cleanup and Drop Log\n")
    log_file.write("=" * 40 + "\n\n")

# Perform the cleanup
delete_files_in_directory(base_dir, patterns)

# Drop the MySQL database
drop_mysql_database(mysql_host, mysql_user, mysql_password, mysql_database)

print("Cleanup completed and database drop attempted. Check the log for details.")
