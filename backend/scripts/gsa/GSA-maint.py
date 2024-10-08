import mysql.connector
import json

# Database connection details
host = "localhost"
user = "whatcheer"
password = "meatwad"
database = "auctions"
table = "gsa"

# Connect to the database
db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Get a cursor to execute SQL queries
cursor = db.cursor()

# SQL query to delete expired rows
sql = "DELETE FROM {} WHERE time_left < NOW()".format(table)

# Execute the query
cursor.execute(sql)

# Get the number of rows deleted
items_removed = cursor.rowcount

# Commit the changes
db.commit()

# Close the connection
cursor.close()
db.close()

print(f"{items_removed} expired rows deleted from the {table} table.")

# Update statistics
try:
    with open('gsa_statistics.json', 'r+') as f:
        stats = json.load(f)
        stats['items_removed'] = items_removed
        f.seek(0)
        json.dump(stats, f)
        f.truncate()
except FileNotFoundError:
    with open('gsa_statistics.json', 'w') as f:
        json.dump({
            "auctions_scraped": 1,  # Assuming one auction is scraped per run
            "items_added": 0,
            "items_updated": 0,
            "items_removed": items_removed,
            "items_skipped": 0,
            "errors": 0,
            "addresses_processed": 0,
            "addresses_updated": 0,
            "addresses_skipped": 0
        }, f)
