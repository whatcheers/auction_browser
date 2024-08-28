import mysql.connector

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

# Commit the changes
db.commit()

# Close the connection
cursor.close()
db.close()

print("Expired rows deleted from the {} table.".format(table))
