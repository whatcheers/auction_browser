import mysql.connector
import json

# Database connection details
host = "localhost"
user = "whatcheer"
password = "meatwad"
database = "auctions"
table = "backes"

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

print(f"Expired rows deleted from the {table} table: {items_removed}")

# Save statistics
with open('backes_statistics.json', 'r+') as f:
    stats = json.load(f)
    stats['items_removed'] = items_removed
    f.seek(0)
    json.dump(stats, f)
    f.truncate()

print(f"Updated statistics: {items_removed} items removed")