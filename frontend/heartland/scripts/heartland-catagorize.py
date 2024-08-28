import json

# Load the JSON data from the file
file_path = 'processed-titles.json'
with open(file_path, 'r') as file:
    items = json.load(file)

# Function to determine the category of an item
def determine_category(item_name, categories):
    for category, keywords in categories.items():
        if any(keyword in item_name for keyword in keywords):
            return category
    return "Miscellaneous Industrial Supplies"

# Categories definition
categories = {
    "Drone and Aerial Equipment": ['drone', 'hexacopter', 'aerial'],
    "Electrical Components and Equipment": ['transformer', 'switch', 'connector', 'relay', 'sensor', 'transducer', 'electrical', 'breaker', 'controller'],
    "Industrial Motors and Pumps": ['motor', 'gear', 'pump', 'hydraulic'],
    "Industrial and Safety Equipment": ['industrial', 'safety', 'valve', 'fan', 'protection', 'light', 'floodlight'],
    "Tools and Hardware": ['anchor', 'printer', 'ribbon', 'tubing', 'crank', 'storage', 'toolbox', 'lanyard'],
    "Electronic and Measurement Devices": ['meter', 'transmitter', 'pc', 'module', 'encoder', 'loop', 'display', 'circuit'],
    "Pneumatic and Hydraulic Equipment": ['pneumatic', 'hydraulic', 'crimper', 'pump', 'valve'],
    "Lighting and Electrical Fixtures": ['led', 'light', 'fixture', 'enclosure'],
    "Miscellaneous Industrial Supplies": ['chain', 'hardware', 'solar', 'generator', 'equipment', 'supplies']
}

# Process each item to determine its category and prepare for JSON output
processed_items = []
for item in items:
    item_name = item['item_name'].lower()
    category = determine_category(item_name, categories)
    # Create a new item dictionary including the category
    new_item = item.copy()  # Assumes 'item' is a dictionary
    new_item['category'] = category
    processed_items.append(new_item)

# Convert the processed items to a JSON string
json_output = json.dumps(processed_items, indent=4)

# Save to a file called 'heartland-import.json'
file_path = 'heartland-import.json'
with open(file_path, 'w') as file:
    file.write(json_output)

print("Data saved to 'heartland-import.json'.")
