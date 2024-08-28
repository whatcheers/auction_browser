import os
import subprocess
import mysql.connector
import logging
import tarfile
import glob
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_script(command):
    try:
        logger.info(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as process_error:
        logger.error(f"Error running {command[0]}: {process_error}")
        raise

def cleanup_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    archive_dir = os.path.join(current_dir, 'archive')
    os.makedirs(archive_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%m%d%H')
    archive_filename = f"archive-{timestamp}.tar.gz"
    archive_path = os.path.join(archive_dir, archive_filename)

    if not os.path.exists(archive_path):
        with tarfile.open(archive_path, "w:gz") as tar:
            auction_files = glob.glob(os.path.join(current_dir, "auction_#*"))
            for file in auction_files:
                tar.add(file, arcname=os.path.basename(file))
                os.remove(file)
        logger.info(f"Created archive {archive_filename} and added {len(auction_files)} files.")
    else:
        logger.info(f"Archive {archive_filename} already exists. Skipping cleanup.")

def delete_expired_auctions(connection):
    try:
        with connection.cursor() as cursor:
            # Retrieve expired auction numbers from wiscosurp_auctions
            cursor.execute("""
                SELECT DISTINCT auction_number
                FROM wiscosurp_auctions
                WHERE time_left < NOW()
            """)
            expired_auctions = [row[0] for row in cursor.fetchall()]

            if expired_auctions:
                # Delete expired auctions from wiscosurp_auctions
                cursor.execute("""
                    DELETE FROM wiscosurp_auctions
                    WHERE auction_number IN (%s)
                """ % ','.join(['%s'] * len(expired_auctions)), tuple(expired_auctions))
                deleted_wiscosurp_count = cursor.rowcount

                # Delete expired auctions from upcoming_wisco_list
                cursor.execute("""
                    DELETE FROM upcoming_wisco_list
                    WHERE auction_number IN (%s)
                """ % ','.join(['%s'] * len(expired_auctions)), tuple(expired_auctions))
                deleted_upcoming_count = cursor.rowcount

                logger.info(f"Deleted {deleted_wiscosurp_count} expired auctions from wiscosurp_auctions.")
                logger.info(f"Deleted {deleted_upcoming_count} expired auctions from upcoming_wisco_list.")
            else:
                logger.info("No expired auctions found.")

            # Delete rows with lot_number = 1 or item_name containing "practice"
            cursor.execute("""
                DELETE FROM wiscosurp_auctions
                WHERE lot_number = '1' OR item_name LIKE '%practice%'
            """)
            deleted_practice_count = cursor.rowcount

            logger.info(f"Deleted {deleted_practice_count} practice or lot number 1 rows from wiscosurp_auctions.")

            connection.commit()

    except mysql.connector.Error as mysql_error:
        logger.error(f"Error deleting expired auctions and cleaning data: {mysql_error}")

def main():
    logger.info("Starting wisco-scrape.py script")

    # Establish MySQL connection
    logger.info("Connecting to MySQL database")
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='whatcheer',
            password='meatwad',
            database='auctions'
        )
        
        if connection.is_connected():
            # Define the relative paths to the scripts
            current_dir = os.path.dirname(os.path.abspath(__file__))
            wisco_list_scrape_script = os.path.join(current_dir, "wisco-list-scrape.py")
            wisco_list_mysql_script = os.path.join(current_dir, "wisco-list-mysql.py")
            node_script = os.path.join(current_dir, "wisco-scrape-individual.js")
            wisco_latlong_script = os.path.join(current_dir, "wisco-latlong.py")

            # Run the wisco-list-scrape.py script
            logger.info("Running wisco-list-scrape.py script")
            run_script(["python3", wisco_list_scrape_script])

            # Run the wisco-list-mysql.py script
            logger.info("Running wisco-list-mysql.py script")
            run_script(["python3", wisco_list_mysql_script])

            # Retrieve auction URLs that haven't been processed
            logger.info("Retrieving unprocessed auction URLs from the database")
            cursor = connection.cursor()
            query = "SELECT url_to_view_items FROM upcoming_wisco_list WHERE processed = 0"
            cursor.execute(query)
            auction_urls = [row[0] for row in cursor.fetchall()]

            logger.info(f"Found {len(auction_urls)} unprocessed auction URLs")

            for url in auction_urls:
                logger.info(f"Processing auction URL: {url}")
                command = ["node", node_script, url]
                run_script(command)

            # Delete expired auctions
            delete_expired_auctions(connection)

            # Run the wisco-latlong.py script
            logger.info("Running wisco-latlong.py script")
            run_script(["python3", wisco_latlong_script])

            # Cleanup auction files
            logger.info("Cleaning up auction files")
            cleanup_files()

            logger.info("Finished wisco-scrape.py script")
    
    except mysql.connector.Error as mysql_connection_error:
        logger.error(f"Error connecting to MySQL database: {mysql_connection_error}")
    
    finally:
        if connection.is_connected():
            logger.info("Closing the database connection")
            connection.close()

if __name__ == "__main__":
    main()