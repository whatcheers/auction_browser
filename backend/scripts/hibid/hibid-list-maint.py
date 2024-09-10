import os
import pymysql
from colorama import Fore, Style
import json  # Ensure this import is present

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'whatcheer',
    'password': 'meatwad',
    'db': 'auctions',
    'charset': 'utf8mb4'
}

# SQL Queries
check_table_sql = """SHOW TABLES LIKE 'hibid_upcoming_auctions';"""
create_table_sql = """
CREATE TABLE IF NOT EXISTS hibid_upcoming_auctions (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    start_date DATE,
    end_date DATE,
    company VARCHAR(255),
    location VARCHAR(255),
    url VARCHAR(255),
    PRIMARY KEY (id)
);
"""
insert_data_sql = """INSERT INTO hibid_upcoming_auctions (title, start_date, end_date, company, location, url)
SELECT title, start_date, end_date, company, location, url
FROM hibid_upcoming_auctions
WHERE end_date >= CURDATE();
"""
delete_old_data_sql = """DELETE FROM hibid_upcoming_auctions
WHERE end_date < CURDATE();
"""
delete_duplicates_sql = """
DELETE a FROM hibid_upcoming_auctions a
JOIN (
    SELECT MIN(id) as id, title, start_date, end_date, company, location, url
    FROM hibid_upcoming_auctions
    GROUP BY title, start_date, end_date, company, location, url
    HAVING COUNT(*) > 1
) b ON a.id > b.id AND a.title = b.title AND a.start_date = b.start_date AND a.end_date = b.end_date AND a.company = b.company AND a.location = b.location AND a.url = b.url;
"""

stats = {
    "items_removed": 0,
    "duplicates_removed": 0
}

try:
    # Connect to the 'auctions' database
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # Create the 'hibid_upcoming_auctions' table if it doesn't exist
    cursor.execute(check_table_sql)
    if not cursor.fetchone():
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"{Fore.GREEN}Table 'hibid_upcoming_auctions' created successfully.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Table 'hibid_upcoming_auctions' already exists.{Style.RESET_ALL}")

    # Insert new data into the 'hibid_upcoming_auctions' table
    cursor.execute(insert_data_sql)
    conn.commit()
    print(f"{Fore.GREEN}Inserted {cursor.rowcount} new rows into the table.{Style.RESET_ALL}")

    # Delete old data from the 'hibid_upcoming_auctions' table
    cursor.execute(delete_old_data_sql)
    conn.commit()
    stats["items_removed"] = cursor.rowcount
    print(f"{Fore.GREEN}Deleted {stats['items_removed']} expired auctions from the table.{Style.RESET_ALL}")

    # Delete duplicate rows from the 'hibid_upcoming_auctions' table
    cursor.execute(delete_duplicates_sql)
    conn.commit()
    stats["duplicates_removed"] = cursor.rowcount
    print(f"{Fore.GREEN}Deleted {stats['duplicates_removed']} duplicate rows from the table.{Style.RESET_ALL}")

except pymysql.MySQLError as e:
    print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

finally:
    # Close connections and cursors
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print(f"{Fore.CYAN}Database connections closed.{Style.RESET_ALL}")

print(f"{Fore.RED}Items removed: {stats['items_removed']}{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Duplicates removed: {stats['duplicates_removed']}{Style.RESET_ALL}")

# Save statistics
with open('hibid_statistics.json', 'r+') as f:
    stats_file = json.load(f)
    stats_file['items_removed'] = stats["items_removed"]
    stats_file['items_skipped'] += stats["duplicates_removed"]
    f.seek(0)
    json.dump(stats_file, f)
    f.truncate()