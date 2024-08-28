import pymysql

def reset_scrape():
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                 user='whatcheer',
                                 password='meatwad',
                                 database='auctions',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Update the rows in the table
            sql = "UPDATE upcoming_wisco_list SET processed = 'N' WHERE Server = 'localhost'"
            cursor.execute(sql)
        
        # Commit changes
        connection.commit()
        print("Rows updated successfully!")
    
    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    reset_scrape()
