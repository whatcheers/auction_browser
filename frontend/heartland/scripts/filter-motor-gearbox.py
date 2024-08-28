import json
import glob
import os

def filter_motors_gearboxes_manufacturers_with_url(json_file_path, output_file_path):
    # Extended list of keywords for electric motors, gearboxes, and specific manufacturers
    keywords = [
        "electric motor", "gear motor", "gear box", "gear reducer", "worm gear", 
        "planetary gear", "dc motors", "ac electric motors", "sealed dc motors", 
        "right angle gear reducer", "worm gear reducer", "planetary gearbox", 
        "c-face gear reducer", "baldor", "sew eurodrive", "bonfiglioli", "motovario"
    ]
    
    try:
        # Load the JSON data
        with open(json_file_path) as f:
            data = json.load(f)

        # Filter items based on extended keywords and manufacturers, including URLs
        filtered_items = [
            {
                "item_name": item["item_name"], 
                "lot_number": item["lot_number"],
                "url": item["url"]
            }
            for item in data
            if any(keyword.lower() in item["item_name"].lower() for keyword in keywords)
        ]

        # Save the filtered items to a new JSON file
        with open(output_file_path, 'w') as outfile:
            json.dump(filtered_items, outfile, indent=4)
        
        print(f"Filtered items saved to {output_file_path}")
    except Exception as e:
        print(f"Error: {e}")

# Find the newest JSON file in the current directory
list_of_files = glob.glob('./*.json')  # Adjust the path as needed.
latest_file = max(list_of_files, key=os.path.getctime)

# Specify the output file path for the extended filter with URLs
output_file_path = "./archive/filter-motors-gearboxes.json"

# Call the function with the path to the latest JSON file
filter_motors_gearboxes_manufacturers_with_url(latest_file, output_file_path)
