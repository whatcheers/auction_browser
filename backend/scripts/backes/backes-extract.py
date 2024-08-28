import os
import json
import shutil
from bs4 import BeautifulSoup
from datetime import datetime

def extract_auction_data(html_file):
    print(f"Extracting data from {html_file}")
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    auction_data = []

    lot_rows = soup.select('.lotRow')
    print(f"Found {len(lot_rows)} lots")
    for lot_row in lot_rows:
        item_name_element = lot_row.select_one('.rowLotTitle')
        if item_name_element:
            item_name = item_name_element.text.strip()
            item_url = 'https://backes.auctioneersoftware.com' + item_name_element.get('href', '')  # Adjusted URL prepend
            print(f"Item Name: {item_name}")
            print(f"Item URL: {item_url}")  # Display the URL for verification
        else:
            item_name = None
            item_url = None  # Handle cases where the URL might not be found
            print("Item Name not found")

        location = soup.select_one('.auctionLocation').text.strip()
        print(f"Location: {location}")

        current_bid_element = lot_row.select_one('.lotTableWinningBidCol div')
        if current_bid_element:
            current_bid = current_bid_element.text.strip().replace('$', '').replace(',', '')
            if 'x' in current_bid:
                current_bid = current_bid.split('x')[0].strip()
            print(f"Current Bid: {current_bid}")
        else:
            current_bid = None
            print("Current Bid not found")

        lot_number_element = lot_row.select_one('.lotTableLotNumberCol div')
        if lot_number_element:
            lot_number = lot_number_element.text.strip()
            print(f"Lot Number: {lot_number}")
        else:
            lot_number = None
            print("Lot Number not found")

        time_left_element = lot_row.select_one('.lotTableEndTimeCol time')
        if time_left_element:
            time_left = time_left_element['datetime']
            time_left_datetime = datetime.fromtimestamp(int(time_left) // 1000)
            time_left_formatted = time_left_datetime.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Time Left: {time_left_formatted}")
        else:
            time_left_formatted = None
            print("Time Left not found")

        auction_data.append({
            'item_name': item_name,
            'location': location,
            'current_bid': float(current_bid) if current_bid else None,
            'lot_number': lot_number,
            'time_left': time_left_formatted,
            'url': item_url  # Add the URL to the dictionary
        })

    return auction_data

def save_to_json(data, output_file):
    print(f"Saving data to {output_file}")
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=2)
    print(f"Data saved to {output_file}")

def get_html_files():
    html_files = [file for file in os.listdir() if file.endswith('.html')]
    return html_files

def move_html_files(html_files):
    archive_dir = './archive'
    os.makedirs(archive_dir, exist_ok=True)
    for html_file in html_files:
        src_path = os.path.join('.', html_file)
        dst_path = os.path.join(archive_dir, html_file)
        shutil.move(src_path, dst_path)
        print(f"Moved {html_file} to {archive_dir}")

def main():
    html_files = get_html_files()
    if html_files:
        all_auction_data = {}
        for html_file in html_files:
            print(f"Processing HTML file: {html_file}")
            auction_data = extract_auction_data(html_file)
            parent_key = html_file[:12]  # Use the first 12 characters of the filename as the parent key
            all_auction_data[parent_key] = auction_data
        save_to_json(all_auction_data, 'auction_data.json')
        move_html_files(html_files)
    else:
        print("No HTML files found in the directory.")

if __name__ == '__main__':
    main()
