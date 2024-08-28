import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init(autoreset=True)

def scroll_to_bottom(driver):
    """Scroll to the bottom of the page to load all dynamic content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_items_from_page(soup, end_date, location):
    """Extract item details from the current page."""
    base_url = "https://smc.prod4.maxanet.auction"
    item_details = []
    item_rows = soup.select('.row.pb-3.mt-2.border-bottom.border')
    for row in item_rows:
        # Extract lot number
        lot_number_element = row.select_one('.Itemlist-Lottitle a')
        lot_number = lot_number_element.get_text(strip=True).replace('Lot -', '').strip() if lot_number_element else ''
        
        # Extract item name
        item_name_element = row.select_one('.catelogList-desc')
        item_name = ' '.join(child.get_text(strip=True) for child in item_name_element.children).strip()[:255] if item_name_element else ''
        
        # Extract current bid
        current_bid_element = row.select_one('.font-bold.text-body span.font-1rem span:nth-child(2)')
        current_bid = current_bid_element.get_text(strip=True) if current_bid_element else '0.00'
        current_bid = '0.00' if current_bid == 'No bid info' else current_bid
        
        # Extract URL and prepend base URL
        url_element = row.select_one('.Itemlist-Lottitle a')
        relative_url = url_element['href'] if url_element else 'URL not found'
        full_url = f"{base_url}{relative_url}"
        
        # Append extracted details to item list
        item_details.append({
            'lot_number': lot_number,
            'item_name': item_name,
            'current_bid': current_bid,
            'location': location,
            'time_left': end_date,
            'url': full_url  # Use the full URL here
        })
    return item_details


def extract_auction_info(driver, auction_url, end_date):
    """Extract all item information from an auction, handling pagination."""
    print(f"{Fore.BLUE}Scraping auction: {auction_url}{Style.RESET_ALL}")
    
    driver.get(auction_url)
    
    # Wait for the loader to disappear
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.ID, "loader-wrapper"))
    )
    
    # Extract the location from the auction details page
    location_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.fa-map-marker-alt + span'))
    )
    location = location_element.text.strip()  # Corrected method to extract text
    print(f"Location found: {location}")
    
    # Find and click the "View Items" button
    view_items_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.public-content-button-style[href*="AuctionItems"]'))
    )
    view_items_button.click()
    
    all_items = []
    page_number = 1
    
    while True:
        print(f"{Fore.BLUE}Processing page {page_number}...{Style.RESET_ALL}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.row.pb-3.mt-2.border-bottom.border'))
        )
        scroll_to_bottom(driver)
        
        # Parse the page content after scrolling
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract items from the current page
        items = extract_items_from_page(soup, end_date, location)
        all_items.extend(items)
        
        # Check if there's a next page by looking for the '>>' button
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.page-item a.page-link i.fa-angle-double-right')
            parent_li = next_button.find_element(By.XPATH, './ancestor::li[1]')
            
            if "disabled" not in parent_li.get_attribute("class"):
                driver.execute_script("arguments[0].click();", next_button)
                page_number += 1
                time.sleep(random.uniform(2, 4))  # Add a delay between page loads
            else:
                break
        except NoSuchElementException:
            print(f"{Fore.BLUE}Reached last page. Total pages processed: {page_number}{Style.RESET_ALL}")
            break
    
    return all_items

# Main execution starts here
if __name__ == "__main__":
    # Load the auction list from the JSON file
    with open('auction_list.json', 'r') as file:
        auctions = json.load(file)

    # List to store all the auction items
    all_items = []

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the Chrome binary path (adjust this path if necessary)
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"

    # Create a WebDriver instance
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Iterate over the auctions
    for auction in auctions:
        print(f"{Fore.GREEN}Processing auction: {auction['auctionName']}{Style.RESET_ALL}")
        try:
            auction_items = extract_auction_info(driver, auction['auctionUrl'], auction['endDate'])
            all_items.extend(auction_items)
            print(f"{Fore.GREEN}Auction {auction['auctionName']} processed successfully. Found {len(auction_items)} items.{Style.RESET_ALL}")
            
            # Add a random delay between auctions to be polite to the server
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            print(f"{Fore.RED}Error processing auction {auction['auctionName']}: {str(e)}{Style.RESET_ALL}")

    # Close the WebDriver
    driver.quit()

    # Save the auction items to a JSON file
    output_file = 'auction_data.json'
    with open(output_file, 'w') as file:
        json.dump(all_items, file, indent=2)

    print(f"{Fore.GREEN}Auction data saved to {output_file}{Style.RESET_ALL}")
