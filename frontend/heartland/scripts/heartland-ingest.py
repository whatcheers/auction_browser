import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime

# Initialize Chrome WebDriver in headless mode
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=chrome_options)
    return driver

# Scroll to the bottom of the page (only once)
def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

# Scrape a single page and save it as an HTML file
def scrape_page(driver, auction_number, page_number):
    url = f"https://www.heartlandrecoveryinc.com/auctions/{auction_number}?page={page_number}"
    driver.get(url)
    scroll_to_bottom(driver)
    html_content = driver.page_source
    output_file_name = f"page_{page_number}.html"
    with open(output_file_name, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
    print(f"Scraped page {page_number} and saved as {output_file_name}")

# Combine HTML files into a single file
def combine_html_files():
    html_files = [f for f in os.listdir() if f.startswith("page_") and f.endswith(".html")]
    html_content = ""
    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as file:
            html_content += file.read()
    combined_html_file = f"{datetime.now().strftime('%m-%d-%Hhr')}_combined_output.html"
    with open(combined_html_file, "w", encoding="utf-8") as combined_file:
        combined_file.write(html_content)
    print(f"Combined HTML file saved as {combined_html_file}")

# Move combined HTML file to the "archive" folder and delete remaining HTML files
def cleanup_files():
    archive_folder = "archive"
    if not os.path.exists(archive_folder):
        os.mkdir(archive_folder)
    combined_file = f"{datetime.now().strftime('%m-%d-%Hhr')}_combined_output.html"
    os.replace(combined_file, os.path.join(archive_folder, combined_file))
    for html_file in os.listdir():
        if html_file.startswith("page_") and html_file.endswith(".html"):
            os.remove(html_file)
    print("Cleanup completed")

# Main function
def main():
    driver = init_driver()
    print("Enter the auction number (e.g., 51 for https://www.heartlandrecoveryinc.com/auctions/51):")
    auction_number = input("This should be an integer. Enter auction number: ")
    num_pages = int(input("Enter the number of pages to scrape: "))
    for page in range(1, num_pages + 1):
        scrape_page(driver, auction_number, page)
    driver.quit()
    combine_html_files()
    cleanup_files()
    # call_heartland_json_script() - This part of the code is not provided here

if __name__ == "__main__":
    main()
