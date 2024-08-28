import requests
from bs4 import BeautifulSoup
import json
import subprocess

# Colors for formatting output
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Define the URL
url = 'https://hibid.com/auctions?zip=52403&miles=100&ipp=100&s=DISTANCE_NEAREST'

try:
    # Send an HTTP GET request to the URL
    print(colors.OKBLUE + 'Sending a GET request to the URL...' + colors.ENDC)
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        print(colors.OKGREEN + 'Request successful. Parsing the HTML content...' + colors.ENDC)
        # Parse the HTML content of the response
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the auction information
        auctions = []
        auction_headers = soup.find_all('app-auction-header')
        for header in auction_headers:
            auction_title = header.find('div', class_='auction-title').text.strip()
            auction_date = header.find('p').text.strip()
            company_name = header.find('h2', class_='company-name').text.strip()
            location = header.find('a', tabindex='1').text.strip()
            auction_url = 'https://hibid.com' + header.find('a', href=True)['href']  # Extract the auction URL
            auctions.append({
                'title': auction_title,
                'date': auction_date,
                'company': company_name,
                'location': location,
                'url': auction_url
            })

        # Save the data to a JSON file
        with open('auctions_data.json', 'w') as json_file:
            json.dump(auctions, json_file, indent=2)
        print(colors.OKGREEN + 'Auction data saved to auctions_data.json' + colors.ENDC)
    else:
        print(colors.FAIL + f'Error: Failed to retrieve data. Status code: {response.status_code}' + colors.ENDC)

except requests.RequestException as e:
    print(colors.FAIL + f'Error: {e}' + colors.ENDC)
except Exception as e:
    print(colors.FAIL + f'Error: {e}' + colors.ENDC)

# Call the hibid-maint.py script
print(colors.OKBLUE + 'Calling the hibid-maint.py script...' + colors.ENDC)
subprocess.run(['python3', 'hibid-list-maint.py'])
print(colors.OKGREEN + 'The hibid-list-maint.py script has been called' + colors.ENDC)
