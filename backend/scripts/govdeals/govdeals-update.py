from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import mysql.connector
import time

# Database connection setup
db_connection = mysql.connector.connect(
    host="localhost",
    user="whatcheer",
    password="meatwad",
    database="auctions_closed"
)
cursor = db_connection.cursor()

# Ensure the 'bids' and 'last_scraped' columns exist in the database
def ensure_columns_exist():
    cursor.execute("SHOW COLUMNS FROM govdeals LIKE 'bids'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE govdeals ADD COLUMN bids INT NULL")
        print("Added 'bids' column to 'govdeals' table.")
        
    cursor.execute("SHOW COLUMNS FROM govdeals LIKE 'last_scraped'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE govdeals ADD COLUMN last_scraped TIMESTAMP NULL")
        print("Added 'last_scraped' column to 'govdeals' table.")

ensure_columns_exist()

# Selenium WebDriver setup
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment for headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_driver_path = "/usr/bin/chromedriver"  # Ensure this path is correct for your system

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

def update_auction_details(auction_id, url):
    try:
        driver.get(url)
        time.sleep(1)  # Allow time for the page and its dynamic content to load

        sold_amount = None
        bids = None

        try:
            sold_amount_element = driver.find_element(By.CSS_SELECTOR, 'div.bid-body p.float-right')
            sold_amount_text = sold_amount_element.text.strip().replace('USD ', '').replace(',', '')
            sold_amount = float(sold_amount_text) if sold_amount_text else None
        except NoSuchElementException:
            print(f"Sold amount not found for auction {auction_id}.")
        except Exception as e:
            print(f"Exception in extracting sold amount for auction {auction_id}: {e}")

        try:
            bids_element = driver.find_element(By.CSS_SELECTOR, 'a.high-bid-status-wrap span.text-medium-blue')
            bids_text = bids_element.text.strip()
            bids = int(bids_text.split()[0]) if bids_text else None
        except NoSuchElementException:
            print(f"Bids not found for auction {auction_id}.")
        except Exception as e:
            print(f"Exception in extracting bids for auction {auction_id}: {e}")

    except Exception as e:
        print(f"Error accessing auction {auction_id}: {e}")
    finally:
        # Update with the current timestamp to mark as processed
        cursor.execute("UPDATE govdeals SET closing_price = %s, bids = %s, last_scraped = CURRENT_TIMESTAMP WHERE id = %s", (sold_amount, bids, auction_id))
        db_connection.commit()
        print(f"Updated auction {auction_id} with sold amount: {sold_amount if sold_amount is not None else 'NULL'} and bids: {bids if bids is not None else 'NULL'} and timestamp.")

def process_auction_urls():
    # Select only auctions that have not been scraped yet (no timestamp)
    cursor.execute("SELECT id, url FROM govdeals WHERE last_scraped IS NULL")
    for auction_id, url in cursor.fetchall():
        update_auction_details(auction_id, url)

    # Cleanup: Remove records with NULL as closing_price
    cursor.execute("DELETE FROM govdeals WHERE closing_price IS NULL")
    db_connection.commit()
    print("Removed auctions with NULL as closing_price.")

    driver.quit()
    cursor.close()
    db_connection.close()

if __name__ == "__main__":
    process_auction_urls()
