import json
import mysql.connector
import re
from datetime import datetime
import os
from colorama import Fore, Style

# Function to parse date range from the provided string
def parse_date_range(date_str):
    if date_str.lower() == 'n/a':
        return None, None
    else:
        date_matches = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', date_str)
        if len(date_matches) == 2:
            start_date = datetime.strptime(date_matches[0], '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.strptime(date_matches[1], '%m/%d/%Y').strftime('%Y-%m-%d')
            return start_date, end_date
        else:
            date_match = re.search(r'Date\(s\) (\d{1,2}/\d{1,2}/\d{4})', date_str)
            if date_match:
                date = datetime.strptime(date_match.group(1), '%m/%d/%Y').strftime('%Y-%m-%d')
                return date, date
            else:
                raise ValueError("Date format not recognized")

# Configuration for MySQL connection
config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

# Paths for the source and archive directories for hibid
archive_directory_hibid = '.'
target_file_name = 'auctions_data.json'

# Define the INSERT statement for the hibid_upcoming_auctions table
add_item = ("INSERT INTO hibid_upcoming_auctions "
            "(title, start_date, end_date, company, location, url) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            "AS new_data "
            "ON DUPLICATE KEY UPDATE "
            "title=new_data.title, "
            "start_date=new_data.start_date, "
            "end_date=new_data.end_date, "
            "company=new_data.company, "
            "location=new_data.location, "
            "url=new_data.url")

# Connect to the MySQL database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Find the latest auctions_data.json file in the archive directory
archive_files = [f for f in os.listdir(archive_directory_hibid) if f.endswith('_auctions_data.json')]
if archive_files:
    latest_file = max(archive_files)
    target_file_path = os.path.join(archive_directory_hibid, latest_file)

    # Load the JSON data from the target file
    with open(target_file_path) as json_file:
        items = json.load(json_file)

    skipped_items = []
    duplicate_items = 0
    successful_items = 0

    # Iterate over the items and insert them into the database
    for item in items:
        try:
            title = item['title']
            date_str = item['date']
            company = item['company']
            location = item['location']
            url = item['url']

            start_date, end_date = parse_date_range(date_str)

            data_item = (title, start_date, end_date, company, location, url)
            cursor.execute(add_item, data_item)
            if cursor.rowcount > 0:
                successful_items += 1
            else:
                duplicate_items += 1
        except Exception as e:
            print(f"{Fore.RED}Error inserting item: {title}. Error: {e}{Style.RESET_ALL}")
            skipped_items.append(item)

    # Commit the changes and close the connection
    cnx.commit()
    cursor.close()
    cnx.close()

    # Print the summary
    print(f"{Fore.GREEN}Successful insertions: {successful_items}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Duplicate items: {duplicate_items}{Style.RESET_ALL}")
    print(f"{Fore.RED}Skipped items: {len(skipped_items)}{Style.RESET_ALL}")
else:
    print(f"{Fore.YELLOW}No auctions_data.json files found in the archive directory.{Style.RESET_ALL}")