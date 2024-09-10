from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import subprocess
from colorama import init, Fore, Style
import argparse
import os
import logging

# Initialize colorama and logging
init()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize statistics
stats = {
    "auctions_scraped": 0,
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0,
    "addresses_processed": 0,
    "addresses_updated": 0,
    "addresses_skipped": 0
}

def extract_auction_number(html):
    soup = BeautifulSoup(html, 'html.parser')
    auction_number_elem = soup.find('div', class_='p-1 auction-item-cardcolor').find('span', class_='font-weight-600 mr-2 text-body')
    if auction_number_elem:
        auction_number_text = auction_number_elem.text.strip()
        match = re.match(r'(#(\d+-\d+)[A-Z])|.*#(\d+-\d+).*', auction_number_text)
        if match:
            auction_number = match.group(2) if match.group(2) else match.group(3)
            auction_number = auction_number.replace('-', '_')
            return f"auctions_{auction_number}"
    return None

def extract_listing_info(listing, auction_number):
    soup = BeautifulSoup(listing, 'html.parser')
    lot_number_elem = soup.find('span', class_='text-body public-item-font-color')
    lot_number_text = lot_number_elem.text.strip() if lot_number_elem else None
    search_result = re.search(r'\d+', lot_number_text) if lot_number_text else None
    lot_number = search_result.group() if search_result else None

    item_title_elem = soup.find('h4', class_='auction-Itemlist-Title')
    item_title = item_title_elem.text.strip() if item_title_elem else None
    item_url_elem = item_title_elem.find('a') if item_title_elem else None
    item_url = item_url_elem['href'] if item_url_elem else None
    if item_url:
        item_url = "https://bid.wisconsinsurplus.com" + item_url

    end_date_elem = soup.find('input', id=lambda x: x and x.endswith('EndDate'))
    end_date = end_date_elem['value'] if end_date_elem else None
    current_bid_elem = soup.find('span', id=lambda x: x and x.startswith('CurrentBidAmount'))
    current_bid_text = current_bid_elem.text.strip() if current_bid_elem else None
    current_bid_amount = None
    if current_bid_text:
        match = re.search(r'\d+\.\d+', current_bid_text)
        if match:
            current_bid_amount = float(match.group())

    seller_info_elem = soup.find(string=re.compile("Seller:"))
    location_address = None
    if seller_info_elem:
        location_address = seller_info_elem.find_next().text.strip()

    return {
        'Auction Number': auction_number,
        'Lot Number': lot_number,
        'Item Title': item_title,
        'Item URL': item_url,
        'End Date': end_date,
        'Current Bid Amount': current_bid_amount,
        'Location Address': location_address
    }

def process_html_file(html_file_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        auction_number = extract_auction_number(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        listings = soup.find_all('div', class_='row pb-3 mt-2 border-bottom border auction-item-cardcolor')

        output_list = []
        for listing in listings:
            listing_info = extract_listing_info(str(listing), auction_number)
            output_list.append(listing_info)

        json_filename = html_file_path.replace('html', 'json')
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(output_list, json_file, indent=4)

        logging.info(f"{Fore.GREEN}Data written to {json_filename}{Style.RESET_ALL}")

        stats["auctions_scraped"] += 1
        stats["items_added"] += len(output_list)

        # Call wisco-scrape-mysql.py script with the --file argument
        try:
            subprocess.run(["python3", "wisco-scrape-mysql.py", "--file", json_filename], check=True)
            delete_html_file(html_file_path)
        except subprocess.CalledProcessError as e:
            logging.error(f"{Fore.RED}Error calling wisco-scrape-mysql.py: {e}{Style.RESET_ALL}")
            stats["errors"] += 1

    except (json.JSONDecodeError, OSError) as e:
        logging.error(f"Error processing HTML file {html_file_path}: {e}")
        stats["errors"] += 1

def delete_html_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f"Deleted HTML file: {file_path}")
    except OSError as e:
        logging.error(f"Error deleting file {file_path}: {e.strerror}")
        stats["errors"] += 1

def process_html_file(html_file_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        auction_number = extract_auction_number(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        listings = soup.find_all('div', class_='row pb-3 mt-2 border-bottom border auction-item-cardcolor')

        output_list = []
        for listing in listings:
            listing_info = extract_listing_info(str(listing), auction_number)
            output_list.append(listing_info)
            stats["items_scraped"] += 1

        json_filename = f'auction_{auction_number}.json'
        with open(json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(output_list, json_file, ensure_ascii=False, indent=2)

        logging.info(f"Processed {html_file_path} and saved to {json_filename}")
        stats["auctions_processed"] += 1

    except Exception as e:
        logging.error(f"Error processing {html_file_path}: {str(e)}")
        stats["errors"] += 1

    try:
        os.remove(html_file_path)
        logging.info(f"Deleted HTML file: {html_file_path}")
    except OSError as e:
        logging.error(f"Error deleting file {html_file_path}: {e.strerror}")
        stats["errors"] += 1

def process_all_html_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('_content.html'):
            process_html_file(os.path.join(directory, filename))

def main():
    parser = argparse.ArgumentParser(description='Process auction HTML files.')
    parser.add_argument('--file', type=str, help='Single HTML file to process')
    parser.add_argument('--file-all', action='store_true', help='Process all HTML files in the current directory')
    args = parser.parse_args()

    if args.file_all:
        process_all_html_files(os.getcwd())
    elif args.file:
        process_html_file(args.file)
    else:
        logging.error("Either --file or --file-all must be specified.")
        stats["errors"] += 1

    # Save statistics
    with open('wisco_extract_statistics.json', 'w') as f:
        json.dump(stats, f)

    logging.info(f"{Fore.BLUE}Wisconsin Surplus Extract Statistics:{Style.RESET_ALL}")
    logging.info(f"Auctions scraped: {stats['auctions_scraped']}")
    logging.info(f"Items added: {stats['items_added']}")
    logging.info(f"Items updated: {stats['items_updated']}")
    logging.info(f"Items removed: {stats['items_removed']}")
    logging.info(f"Items skipped: {stats['items_skipped']}")
    logging.info(f"Errors: {stats['errors']}")
    logging.info(f"Addresses processed: {stats['addresses_processed']}")
    logging.info(f"Addresses updated: {stats['addresses_updated']}")
    logging.info(f"Addresses skipped: {stats['addresses_skipped']}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
