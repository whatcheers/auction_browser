import json
import re
from datetime import datetime
import subprocess
from termcolor import colored

def sanitize_for_mysql(item_name):
    """
    Sanitizes the item name by escaping single quotes and other special characters for MySQL.
    """
    item_name = item_name.replace("'", "\\'")
    return item_name

def parse_and_format_datetime(date_str):
    date_str = re.sub(r'(st|nd|rd|th)', '', date_str)
    try:
        datetime_obj = datetime.strptime(date_str, '%B %d %Y, %I:%M %p')
        return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Error parsing datetime: {e}")
        return None

def shorten_and_sanitize_item_name(item_name):
    patterns_to_remove = [
        r"mdl\. [^,]+, s/n [^,]+",
        r"Withstands Winds Up to \d+ mph,? ?",
        r"up to \d+ Waypoints,? ?",
        r"^\(\d+\) plt\. ",
        r"\(unused/boxed\)",
        r"\(unused/bagged\)",
        r"\(detailed inventory available, posted (soon )?with photos\)",
        r"& Misc\. ",
        r"\(\d+\)$",
        r"\(\d+\)"
    ]
    for pattern in patterns_to_remove:
        item_name = re.sub(pattern, "", item_name)
    item_name = re.sub(r"\s+", " ", item_name).strip(", ")
    item_name = sanitize_for_mysql(item_name)
    if len(item_name) > 250:
        item_name = item_name[:247] + "..."
    return item_name.strip()

def process_json_file(input_path, output_path):
    with open(input_path, 'r') as file:
        data = json.load(file)
    
    lot_numbers_seen = set()
    duplicates = []

    for item in data:
        if item['lot_number'] in lot_numbers_seen:
            duplicates.append(item['lot_number'])
            continue
        lot_numbers_seen.add(item['lot_number'])
        item['item_name'] = shorten_and_sanitize_item_name(item['item_name'])
        if 'time_left' in item:
            item['time_left'] = parse_and_format_datetime(item['time_left'])

    with open(output_path, 'w') as file:
        json.dump([item for item in data if item['lot_number'] not in duplicates], file, indent=4)

    if duplicates:
        print(colored(f"Skipped duplicates for lot numbers: {', '.join(duplicates)}", "yellow"))
    else:
        print(colored("No duplicates found. All items processed successfully.", "green"))

    print(colored(f"Processed and sanitized JSON file has been saved to '{output_path}'.", "green"))

# Update these paths as necessary
input_path = 'all_items.json'
output_path = 'processed-titles.json'
process_json_file(input_path, output_path)

# Call heartland-mysql.py at the end of the script
subprocess.run(["python3", "heartland-catagorize.py"])
