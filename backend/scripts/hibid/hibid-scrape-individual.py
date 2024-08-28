from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys
import datetime
import os
import logging
import traceback
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import subprocess
import mysql.connector
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("scraper.log"),
                        logging.StreamHandler()
                    ])

# Database connection parameters
db_config = {
    'user': 'whatcheer',
    'password': 'meatwad',
    'host': 'localhost',
    'database': 'auctions',
    'raise_on_warnings': True,
}

def check_auction_active(driver):
    """Check if the auction is currently open for bidding."""
    try:
        # Look for the auction status badge
        status_badge = driver.find_element(By.XPATH, "//div[@id='auction-ststus-badges']//a[contains(@class, 'badge-success')]")
        status_text = status_badge.text.strip()

        if "Bidding Open" in status_text:
            logging.info(f"{Fore.GREEN}Auction is currently open for bidding. Proceeding with scraping.{Style.RESET_ALL}")
            return True
        else:
            logging.info(f"{Fore.YELLOW}Bidding is not open yet. Status: {status_text}. Skipping.{Style.RESET_ALL}")
            return False

    except NoSuchElementException:
        # If we can't find the "Bidding Open" badge, check for countdown
        try:
            countdown_badge = driver.find_element(By.XPATH, "//div[@id='auction-ststus-badges']//div[contains(@class, 'badge-success')]")
            countdown_text = countdown_badge.text.strip()
            if "Bidding opens in" in countdown_text:
                logging.info(f"{Fore.YELLOW}Auction has not started yet. {countdown_text}. Skipping.{Style.RESET_ALL}")
            else:
                logging.info(f"{Fore.YELLOW}Unclear auction status. Status text: {countdown_text}. Skipping to be safe.{Style.RESET_ALL}")
            return False
        except NoSuchElementException:
            logging.warning(f"{Fore.RED}Could not find auction status badge. Skipping auction.{Style.RESET_ALL}")
            return False

    except Exception as e:
        logging.error(f"{Fore.RED}Error while checking auction status: {e}{Style.RESET_ALL}")
        return False

def main_scraper(auction_url, page_number, file):
    logging.info(f"{Fore.BLUE}Scraping page {page_number}{Style.RESET_ALL}")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_driver_path = "/usr/bin/chromedriver"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        current_page_url = f"{auction_url}?apage={page_number}&ipp=100"
        logging.debug(f"{Fore.CYAN}Navigating to {current_page_url}{Style.RESET_ALL}")
        driver.get(current_page_url)
        driver.implicitly_wait(10)

        # Check if auction has started
        if not check_auction_active(driver):
            return False

        # Scroll down the page to ensure all dynamic content is loaded
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)  # Sleep to allow page content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html = driver.page_source
        # Append the scraped content to the same file
        file.write(f"\n<!-- Page {page_number} -->\n")
        file.write(html)

        # Check for the presence of the "Next" button using the exact structure provided
        try:
            next_button = driver.find_element(By.XPATH, "//a[.//span[contains(text(), 'Next') or contains(text(), '>')]]")
            has_next_page = True
        except NoSuchElementException:
            has_next_page = False

        return has_next_page

    except Exception as e:
        logging.error(f"{Fore.RED}An error occurred during scraping: {e}{Style.RESET_ALL}")
        logging.error(traceback.format_exc())
        return False
    finally:
        driver.quit()
        logging.info(f"{Fore.GREEN}Scraped finished{Style.RESET_ALL}")

def main():
    try:
        # Connect to the MySQL database
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Load the list of processed auction URLs from a file
        processed_urls_file = "processed_urls.txt"
        if os.path.exists(processed_urls_file):
            with open(processed_urls_file, "r") as f:
                processed_urls = set(line.strip() for line in f)
        else:
            processed_urls = set()

        cursor.execute("SELECT url FROM hibid_upcoming_auctions")
        auction_urls = [row[0] for row in cursor.fetchall()]

        for auction_url in auction_urls:
            if auction_url in processed_urls:
                logging.info(f"{Fore.YELLOW}URL already processed: {auction_url}{Style.RESET_ALL}")
                continue

            logging.info(f"{Fore.BLUE}Starting scraper for URL: {auction_url}{Style.RESET_ALL}")
            page_number = 1
            now = datetime.datetime.now()
            file_name = f"scrape-{now.strftime('%Y-%m-%d-%H-%M')}.html"
            with open(file_name, 'w', encoding='utf-8') as file:
                while True:
                    has_next_page = main_scraper(auction_url, page_number, file)
                    if not has_next_page:
                        break
                    page_number += 1

            subprocess.run(["python3", "hibid-scrape-parse.py", file_name])
            processed_urls.add(auction_url)
            with open(processed_urls_file, "a") as f:
                f.write(auction_url + "\n")

    except mysql.connector.Error as e:
        logging.error(f"{Fore.RED}Error connecting to the database: {e}{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        logging.error(traceback.format_exc())
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals():
            cnx.close()

if __name__ == "__main__":
    main()
