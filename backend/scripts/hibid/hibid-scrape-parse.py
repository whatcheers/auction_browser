from bs4 import BeautifulSoup
import datetime
import json
import os
import subprocess
from colorama import init, Fore, Style
import sys
from datetime import datetime, timedelta

init(autoreset=True)

def log(message, color=Fore.WHITE):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} {color + message}")

def convert_countdown_to_datetime(countdown):
    if countdown is None:
        return None

    parts = countdown.strip().split()
    days = hours = minutes = 0

    for part in parts:
        if part.endswith('d'):
            days = int(part[:-1])
        elif part.endswith('h'):
            hours = int(part[:-1])
        elif part.endswith('m'):
            minutes = int(part[:-1])
        else:
            log(f"Unexpected format in countdown string: {part}", Fore.RED)
            continue

    time_left = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
    return time_left


base_url = "https://hibid.com/"

def parse_html_content(file_path):
    log("Opening file for parsing: " + file_path, Fore.YELLOW)
    try:
        with open(file_path, "r") as file:
            html_content = file.read()
    except FileNotFoundError:
        log(f"Error: File not found: {file_path}", Fore.RED)
        log_skipped_item(file_path, "File not found")
        return []
    except Exception as e:
        log(f"Error reading file: {file_path} - {e}", Fore.RED)
        log_skipped_item(file_path, str(e))
        return []

    if not html_content.strip():
        log(f"Skipping empty HTML file: {file_path}", Fore.YELLOW)
        log_skipped_item(file_path, "Empty HTML file")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    parsed_data = []

    company_name_element = soup.find("h2", class_="company-name")
    if company_name_element and company_name_element.find("a"):
        company_name = company_name_element.find("a").text.strip()
    else:
        company_name = "Unknown Company"

    log("Parsing HTML content...", Fore.YELLOW)
    for lot in soup.find_all("app-lot-tile"):
        lot_number_element = lot.find("span", class_="text-primary fw-bold ng-star-inserted")
        lot_number = lot_number_element.text.strip() if lot_number_element else "N/A"

        bids_element = lot.find("a", class_="lot-bid-history btn-link ng-star-inserted")
        number_of_bids = bids_element.text.strip() if bids_element else "N/A"

        time_left_element = lot.find("div", class_="inline-block lot-time-left text-wrap")
        if time_left_element:
            time_left = time_left_element.text.strip()
            time_left = convert_countdown_to_datetime(time_left)
        else:
            auction_info_element = soup.find("div", class_="col")
            if auction_info_element:
                date_element = auction_info_element.find("p", string=lambda text: "Date(s)" in text)
                if date_element:
                    date_range = date_element.text.strip().split("Date(s)")[1].strip()
                    closing_date = date_range.split("-")[1].strip() if len(date_range.split("-")) > 1 else None
                    time_left = datetime.strptime(closing_date, "%m/%d/%Y") if closing_date else None
                else:
                    time_left = None
            else:
                time_left = None

        url_element = lot.find("a", class_="lot-number-lead lot-link lot-title-ellipsis lot-preview-link link mb-1 ng-star-inserted")
        url = base_url + url_element['href'] if url_element and 'href' in url_element.attrs else "N/A"

        item_name_element = lot.find("h2", class_="lot-title")
        item_name = item_name_element.text.strip() if item_name_element else "N/A"

        current_bid_price_element = lot.find("span", class_="lot-high-bid")
        current_bid_price = current_bid_price_element.text.split()[-2] if current_bid_price_element else "x"

        # Extracting location information
        location_element = soup.find("div", class_="hovertext")
        if location_element:
            location_link = location_element.find("a")['href']
            location = location_element.find("a").text.strip()
        else:
            location_link = "N/A"
            location = "N/A"

        # Handle the 'x' placeholder in current_bid_price
        if current_bid_price == 'x':
            current_bid_price = 0
        else:
            try:
                current_bid_price = int(current_bid_price.replace(',', ''))
            except ValueError:
                current_bid_price = 0

        parsed_data.append({
            "lot_number": lot_number,
            "number_of_bids": number_of_bids,
            "time_left": time_left,
            "url": url,
            "item_name": item_name,
            "current_bid_price": current_bid_price,
            "company_name": company_name,
            "location_link": location_link,
            "location": location
        })

    return parsed_data

def save_to_json(parsed_data, output_filename):
    log("Saving parsed data to JSON file: " + output_filename, Fore.YELLOW)
    with open(output_filename, 'w') as json_file:
        json.dump(parsed_data, json_file, indent=4, default=str)
    log("Data successfully saved to " + output_filename, Fore.GREEN)

def get_output_filename(input_filepath):
    directory, filename = os.path.split(input_filepath)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_parsed.json"
    return os.path.join(directory, output_filename)

def log_skipped_item(file_path, reason):
    with open("skipped_items.log", "a") as log_file:
        log_file.write(f"Skipped file: {file_path} - Reason: {reason}\n")
    log(f"Skipped file: {file_path} - Reason: {reason}", Fore.YELLOW)

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        log("Starting to process file: " + file_path, Fore.GREEN)
        parsed_data = parse_html_content(file_path)
        output_filename = get_output_filename(file_path)
        save_to_json(parsed_data, output_filename)
        log("All operations completed successfully.", Fore.GREEN)
        subprocess.run(["python3", "hibid-scrape-import.py"])  # Adjust path if necessary
    else:
        log("No file path provided. Exiting.", Fore.RED)

if __name__ == "__main__":
    main()
