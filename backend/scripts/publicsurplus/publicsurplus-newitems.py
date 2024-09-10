import os
import sys
import time
import json
import logging
import concurrent.futures
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
import random

# ANSI escape codes for colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def create_search_url(page_number, search_params):
    base_url = "https://www.publicsurplus.com/sms/browse/search?"
    params = {
        'posting': 'y',
        'page': page_number,
        'milesLocation': search_params['miles_location'],
        'zipCode': search_params['zip_code'],
        'search': 'Search'
    }
    search_url = base_url + "&".join(f"{key}={value}" for key, value in params.items())
    return search_url

def initialize_webdriver():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        # Add more user agents as needed
    ]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    chrome_driver_path = "/usr/bin/chromedriver"
    
    try:
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"{Colors.FAIL}Error initializing WebDriver: {e}{Colors.ENDC}")
        sys.exit(1)

def parse_time_left(time_left_str):
    days_match = re.search(r'(\d+)\s*days?', time_left_str)
    hours_match = re.search(r'(\d+)\s*hrs?', time_left_str)
    minutes_match = re.search(r'(\d+)\s*min?', time_left_str)
    days = int(days_match.group(1)) if days_match else 0
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    return timedelta(days=days, hours=hours, minutes=minutes)

def get_expiration_datetime(time_left_str):
    current_datetime = datetime.now()
    time_delta = parse_time_left(time_left_str)
    expiration_datetime = current_datetime + time_delta
    return expiration_datetime.strftime('%m/%d/%Y %H:%M')

def extract_pickup_location(driver, auction_detail_url, auction_id):
    print(f"{Colors.OKBLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extracting pickup location for Auction ID: {auction_id}{Colors.ENDC}")
    driver.get(auction_detail_url)
    time.sleep(random.uniform(1, 3))  # Dynamic sleep time
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find the <i> element with data-bs-original-title="Pick-up Location"
    location_icon = soup.find('i', {'data-bs-original-title': 'Pick-up Location'})
    if location_icon:
        # Navigate to the parent elements to find the location details
        location_div = location_icon.find_parent('div', class_='icon-info-common')
        if location_div:
            location_text = location_div.find_all('div')[2].get_text(separator=" ").strip()
            return location_text
    return "Location not found"

def scrape_page(url, search_params):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('scrape_page.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.debug(f"Processing URL: {url}")
    print(f"{Colors.OKBLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing URL: {url}{Colors.ENDC}")

    driver = initialize_webdriver()
    driver.get(url)
    time.sleep(random.uniform(1, 3))  # Dynamic sleep time

    current_page_data = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    auction_rows = soup.find_all('tr')[1:]  # Assuming the first row is headers

    # Log the page source and the list of auction rows
    logger.debug(f"Page source: {driver.page_source}")
    logger.debug(f"Auction rows: {auction_rows}")

    print(f"{Colors.OKBLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found {len(auction_rows)} auction rows{Colors.ENDC}")

    for row in auction_rows:
        columns = row.find_all('td')
        if len(columns) >= 6:
            auction_detail_url = 'https://www.publicsurplus.com' + columns[1].find('a')['href']
            auction_id = columns[0].text.strip()

            print(f"{Colors.OKBLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing Auction ID: {auction_id}{Colors.ENDC}")

            location = extract_pickup_location(driver, auction_detail_url, auction_id)
            time_left_str = columns[4].text.strip()
            auction_item = {
                "id": auction_id,
                "item_name": columns[1].text.strip(),
                "location": location,
                "current_bid": columns[5].text.strip().replace('$', '').replace(',', ''),
                "lot_number": auction_id,
                "time_left": get_expiration_datetime(time_left_str),
                "url": auction_detail_url,
            }
            current_page_data.append(auction_item)
            print(f"{Colors.OKGREEN}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processed Auction ID: {auction_id}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Skipping row due to insufficient columns{Colors.ENDC}")

    driver.quit()

    logger.debug(f"Finished processing URL: {url}")
    print(f"{Colors.OKGREEN}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Finished processing URL: {url}{Colors.ENDC}")
    logger.removeHandler(file_handler)
    file_handler.close()

    return current_page_data

def scrape_auctions_parallel(search_params, max_pages=None):
    all_auction_data = []
    page_numbers = list(range(0, max_pages)) if max_pages else []

    with ThreadPoolExecutor(max_workers=3) as executor:  # Limit to 3 workers
        futures = []
        for page_number in page_numbers:
            url = create_search_url(page_number, search_params)
            print(f"{Colors.OKBLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Submitting task for page: {page_number}{Colors.ENDC}")
            futures.append(executor.submit(scrape_page, url, search_params))

        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    all_auction_data.extend(data)
                else:
                    print(f"{Colors.WARNING}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No data found on page.{Colors.ENDC}")
            except Exception as exc:
                print(f"{Colors.FAIL}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Page generated an exception: {exc}{Colors.ENDC}")

    return all_auction_data

def main(search_params):
    print(f"{Colors.HEADER}Initializing WebDriver...{Colors.ENDC}")
    driver = initialize_webdriver()
    print(f"{Colors.OKGREEN}WebDriver initialized.{Colors.ENDC}")

    try:
        auction_data = scrape_auctions_parallel(search_params, max_pages=10)
        print(f"{Colors.OKGREEN}Scraping completed successfully.{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Total auctions scraped: {len(auction_data)}{Colors.ENDC}")

        if not auction_data:
            print(f"{Colors.WARNING}No auctions found. Exiting with code 1.{Colors.ENDC}")
            sys.exit(1)
    finally:
        print(f"{Colors.FAIL}Closing the WebDriver...{Colors.ENDC}")
        driver.quit()
        print(f"{Colors.OKGREEN}WebDriver closed.{Colors.ENDC}")

    # Save to JSON
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    archive_dir = "./archive"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    json_filename = os.path.join(archive_dir, f"consolidated-{current_datetime}.json")
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(auction_data, json_file, indent=4)

    print(f"{Colors.OKBLUE}Data has been written to {json_filename}{Colors.ENDC}")

    # Save statistics
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
    stats["auctions_scraped"] = len(auction_data)
    with open('publicsurplus_newitems_statistics.json', 'w') as f:
        json.dump(stats, f)

if __name__ == "__main__":
    search_params = {
        'miles_location': '200',
        'zip_code': '52403'
    }
    main(search_params)

def main(search_params):
    print(f"{Colors.HEADER}Initializing WebDriver...{Colors.ENDC}")
    driver = initialize_webdriver()
    print(f"{Colors.OKGREEN}WebDriver initialized.{Colors.ENDC}")

    try:
        auction_data = scrape_auctions_parallel(search_params, max_pages=10)
        print(f"{Colors.OKGREEN}Scraping completed successfully.{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Total auctions scraped: {len(auction_data)}{Colors.ENDC}")

        if not auction_data:
            print(f"{Colors.WARNING}No auctions found. Exiting with code 1.{Colors.ENDC}")
            sys.exit(1)
    finally:
        print(f"{Colors.FAIL}Closing the WebDriver...{Colors.ENDC}")
        driver.quit()
        print(f"{Colors.OKGREEN}WebDriver closed.{Colors.ENDC}")

    # Save to JSON
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    archive_dir = "./archive"
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    json_filename = os.path.join(archive_dir, f"consolidated-{current_datetime}.json")
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(auction_data, json_file, indent=4)

    print(f"{Colors.OKBLUE}Data has been written to {json_filename}{Colors.ENDC}")

if __name__ == "__main__":
    search_params = {
        'miles_location': '200',
        'zip_code': '52403'
    }
    main(search_params)
