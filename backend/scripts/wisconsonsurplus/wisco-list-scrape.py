import os
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

# Colors for formatting output
class colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

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

def update_statistics():
    try:
        with open('wisco_statistics.json', 'r') as f:
            existing_stats = json.load(f)
        for key in stats:
            existing_stats[key] = (existing_stats.get(key, 0) or 0) + stats[key]
        with open('wisco_statistics.json', 'w') as f:
            json.dump(existing_stats, f, indent=2)
    except FileNotFoundError:
        with open('wisco_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)

print(f"{colors.HEADER}Starting the script...{colors.ENDC}")

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")  # Run in headless mode

# Setup service to enable verbose logging
service = Service(executable_path="/usr/bin/chromedriver", log_path=sys.stderr, service_args=["--verbose"])

# Initialize the driver with the specified service and options
driver = webdriver.Chrome(service=service, options=chrome_options)

print(f"{colors.OKGREEN}WebDriver initialized.{colors.ENDC}")

# Navigate to the Wisconsin Surplus current auctions page
print(f"{colors.HEADER}Navigating to the Wisconsin Surplus current auctions page...{colors.ENDC}")
driver.get("https://wisconsinsurplus.com/current-auctions/")

# Wait for the page to load
print(f"{colors.HEADER}Waiting for the page to load...{colors.ENDC}")
time.sleep(8)  # Adjust the wait time according to your needs

# Scroll down the page to load all auctions
print(f"{colors.HEADER}Scrolling down the page to load all auctions...{colors.ENDC}")
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Initialize a list to store auction data
auctions_data = []

# Extract the details based on the provided HTML structure
try:
    print(f"{colors.HEADER}Extracting auction details...{colors.ENDC}")
    auction_elements = driver.find_elements(By.CSS_SELECTOR, "div.ua-txt")
    for auction_element in auction_elements:
        auction_name = auction_element.find_element(By.CSS_SELECTOR, "h2").text
        auction_closing_date = auction_element.find_element(By.CSS_SELECTOR, "h6").text.replace("Auction Starts Closing: ", "")
        details_url = auction_element.find_element(By.CSS_SELECTOR, "a.d-link").get_attribute('href')
        view_items_url = auction_element.find_element(By.CSS_SELECTOR, "a.v-link").get_attribute('href')

        # New logic to extract and format auction number and name
        auction_number_match = re.match(r"#\d{2}-\d{3}", auction_name)
        auction_number = auction_number_match.group(0) if auction_number_match else ""
        formatted_auction_name = re.sub(r"^#\d{2}-\d{3} - ", "", auction_name)

        # Extract location from the auction name using regex
        location_match = re.search(r' - (.+?),?$', formatted_auction_name)
        location = location_match.group(1) if location_match else ""

        # Create a dictionary for the current auction with auction number
        auction_data = {
            "Auction Number": auction_number,
            "Auction Name": formatted_auction_name,
            "Location": location,
            "Auction Closing Date": auction_closing_date,
            "URL for Auction Details": details_url,
            "URL to View Items": view_items_url
        }

        auctions_data.append(auction_data)
    
    stats["auctions_scraped"] = len(auctions_data)
    print(f"{colors.OKGREEN}Successfully scraped {stats['auctions_scraped']} auctions.{colors.ENDC}")
except Exception as e:
    print(f"{colors.FAIL}Error during extraction: {e}{colors.ENDC}")
    stats["errors"] += 1
finally:
    # Don't forget to close the driver after your scraping job is done
    driver.quit()

    # Save the auction data to a JSON file
    with open("auctions_data.json", "w") as f:
        json.dump(auctions_data, f, indent=4)

    print(f"{colors.OKGREEN}Auction data saved to auctions_data.json{colors.ENDC}")

    # Save statistics
    update_statistics()
    print(f"{colors.OKGREEN}Statistics saved to wisco_statistics.json{colors.ENDC}")
    print(f"{colors.HEADER}Wisconsin Surplus List Scraping Statistics:{colors.ENDC}")
    print(f"Auctions scraped: {stats['auctions_scraped']}")
    print(f"Errors: {stats['errors']}")