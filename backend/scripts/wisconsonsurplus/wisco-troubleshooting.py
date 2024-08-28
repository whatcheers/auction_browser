import mysql.connector

def fetch_unprocessed_auctions():
    # MySQL connection details
    db_config = {
        'user': 'whatcheer',
        'password': 'meatwad',
        'host': 'localhost',
        'database': 'auctions'
    }

    # Connect to MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # SQL query to fetch all auctions with processed = 0
    query = """
        SELECT auction_number, auction_name, location, auction_closing_date, url_to_view_items
        FROM upcoming_wisco_list
        WHERE processed = 0
    """
    cursor.execute(query)
    unprocessed_auctions = cursor.fetchall()

    # Display results in a more readable format
    if unprocessed_auctions:
        print("Unprocessed Auctions:")
        print("Auction Number | Auction Name | Location | Closing Date | URL")
        print('-' * 120)
        for auction in unprocessed_auctions:
            print(f"{auction[0]} | {auction[1]} | {auction[2]} | {auction[3]} | {auction[4]}")
    else:
        print("No unprocessed auctions found.")

    # Prompt the user to choose an auction
    auction_number = input("\nEnter the Auction Number to process or 'q' to quit: ")

    if auction_number.lower() != 'q':
        # Find the URL for the selected auction
        selected_auction = next((auction for auction in unprocessed_auctions if auction[0] == auction_number), None)
        if selected_auction:
            run_node_script(selected_auction[4])
        else:
            print("Invalid Auction Number.")

    # Close the cursor and connection
    cursor.close()
    connection.close()

def run_node_script(url):
    import subprocess

    # Node script path
    node_script = "wisco-scrape-individual.js"

    try:
        # Run the Node.js script with the auction URL
        subprocess.run(["node", node_script, url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

if __name__ == '__main__':
    fetch_unprocessed_auctions()
