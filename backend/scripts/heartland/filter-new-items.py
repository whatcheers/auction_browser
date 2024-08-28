import json
import glob
import os

def filter_new_items(json_file_path, output_file_path):
    # Keywords to search for in item descriptions
    keywords = ["new", "unused", "unboxed", "NOS"]
    
    try:
        # Load the JSON data
        with open(json_file_path) as f:
            data = json.load(f)

        # Filter items based on condition keywords
        new_items = [
            {"item_name": item["item_name"], "lot_number": item["lot_number"]}
            for item in data
            if any(keyword in item["item_name"].lower() for keyword in keywords)
        ]

        # Save the filtered items to a new JSON file
        with open(output_file_path, 'w') as outfile:
            json.dump(new_items, outfile, indent=4)
        
        print(f"Filtered items saved to {output_file_path}")
    except Exception as e:
        print(f"Error: {e}")

# Find the newest JSON file in the current directory
list_of_files = glob.glob('./*.json')  # You might need to adjust the path.
latest_file = max(list_of_files, key=os.path.getctime)

# Specify the output file path
output_file_path = "./archive/filtered_new_items.json"

# Call the function with the path to the latest JSON file
filter_new_items(latest_file, output_file_path)
