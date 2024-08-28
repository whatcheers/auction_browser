import re
import os
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

# Define the path to the directory containing the HTML file.
directory_path = "."

def find_newest_html_file(directory):
    try:
        html_files = [file for file in os.listdir(directory) if file.endswith(".html")]
        newest_file = max(html_files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))
        return os.path.join(directory, newest_file)
    except Exception as e:
        print(f"Error finding the newest HTML file: {e}")
        return None

def extract_data(soup):
    auction_data = []
    listings = soup.find_all("div", class_="card-body")
    
    # Initialize a progress bar
    progress_bar = tqdm(total=len(listings), desc="Extracting data", unit="listing")

    error_count = 0

    for listing in listings:
        try:
            title_tag = listing.find("a", class_="link-click")
            title = title_tag.text.strip() if title_tag else "No title"
            title = re.sub(r'[^\w\s]', '', title)
            relative_url = title_tag.get("href") if title_tag else "#"
            absolute_url = f"https://www.govdeals.com{relative_url}"

            location_tag = listing.find('p', class_='card-grey')
            location = location_tag.text.strip() if location_tag else 'Not specified'
            
            current_bid_tag = listing.find('p', class_='card-amount')
            current_bid = current_bid_tag.text.strip().split('$')[-1] if current_bid_tag else 'Not specified'
            
            lot_number = 'Not specified'
            for p_tag in listing.find_all('p', class_='card-grey'):
                if 'Lot#:' in p_tag.text:
                    lot_number = p_tag.text.split('Lot#:')[-1].strip()
                    break
            
            time_left_tag = listing.find('app-ux-timer')
            time_left = time_left_tag.text.strip() if time_left_tag else 'Not specified'

            auction_data.append({
                "Title": title,
                "URL": absolute_url,
                "Location": location,
                "Current Bid": current_bid,
                "Lot Number": lot_number,
                "Time Left": time_left,
            })
        except Exception as e:
            error_message = str(e)
            # Check if the error message is not the specific MySQL warning
            if "1287: 'VALUES function' is deprecated" not in error_message:
                with open('import-errors.txt', 'a') as error_log:
                    error_log.write(f"Error extracting data from listing: {error_message}\n")
                error_count += 1
            # If it is the MySQL warning, we simply pass
            pass
        
        # Update the progress bar
        progress_bar.update(1)
    
    # Close the progress bar
    progress_bar.close()

    # Print the summary of errors that were logged (excluding the specific MySQL warning)
    print(f"{len(listings) - error_count} listings processed successfully.")
    print(f"{error_count} errors logged to import-errors.txt (excluding specific MySQL warning).")

    return auction_data

file_path = find_newest_html_file(directory_path)
if file_path:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        auction_data = extract_data(soup)
        json_file_path = "auction_data.json"
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(auction_data, json_file, ensure_ascii=False, indent=4)
        print(f"Total Listings Found: {len(auction_data)}")
        print(f"Auction data has been written to {json_file_path}")
    except Exception as e:
        print(f"Error processing the file {file_path}: {e}")
else:
    print("No HTML file found or an error occurred finding the newest file.")
