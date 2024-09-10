import os
import subprocess
import json
from datetime import datetime
import re

# Function to strip ANSI color codes
def strip_ansi_codes(s):
    return re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', s)

# Function to safely parse integer values
def safe_int_parse(value):
    try:
        return int(strip_ansi_codes(value))
    except ValueError:
        return 0

# Initialize statistics
stats = {
    "auctions_scraped": 1,  # Assuming one auction is scraped per run
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0,
    "addresses_processed": 0,
    "addresses_updated": 0,
    "addresses_skipped": 0
}

# Delete all HTML files in the current directory
html_files = [file for file in os.listdir('.') if file.endswith('.html')]
for file in html_files:
    os.remove(file)

# List of scripts to run
scripts = [
    "hibid-list-scrape.py",
    "hibid-list-mysql.py",
    "hibid-scrape-individual.py",
    "hibid-scrape-parse.py",
    "hibid-scrape-import.py",
    "hibid-latlong.py",
    "hibid-list-maint.py"
]

# Run each script
for script in scripts:
    try:
        result = subprocess.run(["python3", script], capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # Parse statistics from script output
        lines = result.stdout.split('\n')
        for line in lines:
            line = line.lower()
            if "items added:" in line:
                stats["items_added"] += safe_int_parse(line.split(':')[1].strip())
            elif "items updated:" in line:
                stats["items_updated"] += safe_int_parse(line.split(':')[1].strip())
            elif "items removed:" in line:
                stats["items_removed"] += safe_int_parse(line.split(':')[1].strip())
            elif "items skipped:" in line:
                stats["items_skipped"] += safe_int_parse(line.split(':')[1].strip())
            elif "duplicates removed:" in line:
                stats["items_removed"] += safe_int_parse(line.split(':')[1].strip())
            elif "errors:" in line:
                stats["errors"] += safe_int_parse(line.split(':')[1].strip())
            elif "addresses processed:" in line:
                stats["addresses_processed"] += safe_int_parse(line.split(':')[1].strip())
            elif "addresses updated:" in line:
                stats["addresses_updated"] += safe_int_parse(line.split(':')[1].strip())
            elif "addresses skipped:" in line:
                stats["addresses_skipped"] += safe_int_parse(line.split(':')[1].strip())
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}:")
        print(e.stderr)
        stats["errors"] += 1

# Save statistics
with open('hibid_statistics.json', 'w') as f:
    json.dump(stats, f)

# Print statistics
print("\nHiBid Scraping Statistics:")
print(f"Auctions scraped: {stats['auctions_scraped']}")
print(f"Items added: {stats['items_added']}")
print(f"Items updated: {stats['items_updated']}")
print(f"Items removed: {stats['items_removed']}")
print(f"Items skipped: {stats['items_skipped']}")
print(f"Errors: {stats['errors']}")
print(f"Addresses processed: {stats['addresses_processed']}")
print(f"Addresses updated: {stats['addresses_updated']}")
print(f"Addresses skipped: {stats['addresses_skipped']}")

# Output statistics in the format expected by the orchestrator
print(json.dumps({"hibid-scrape.py": stats}))