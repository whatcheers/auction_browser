import subprocess
import json

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {command[0]}:")
        print(result.stderr)

run_command(["node", "bidspotter-list.js"])
run_command(["python3", "bidspotter-mysql.py"])
run_command(["python3", "bidspotter-latlong.py"])
run_command(["python3", "bidspotter-maint.py"])

# Read and print statistics
try:
    with open('bidspotter_statistics.json', 'r') as f:
        stats = json.load(f)
    
    print("\nBidspotter Scraping Statistics:")
    print(f"Auctions scraped: {stats.get('auctions_scraped', 0)}")
    print(f"Items added: {stats.get('items_added', 0)}")
    print(f"Items updated: {stats.get('items_updated', 0)}")
    print(f"Items removed: {stats.get('items_removed', 0)}")
    print(f"Items skipped: {stats.get('items_skipped', 0)}")
    print(f"Errors: {stats.get('errors', 0)}")
    print(f"Addresses processed: {stats.get('addresses_processed', 0)}")
    print(f"Addresses updated: {stats.get('addresses_updated', 0)}")
    print(f"Addresses skipped: {stats.get('addresses_skipped', 0)}")

    # Output statistics in the format expected by the orchestrator
    print(json.dumps({
        "bidspotter-scrape.py": {
            "auctions_scraped": stats.get('auctions_scraped', 0),
            "items_added": stats.get('items_added', 0),
            "items_updated": stats.get('items_updated', 0),
            "items_removed": stats.get('items_removed', 0),
            "items_skipped": stats.get('items_skipped', 0),
            "errors": stats.get('errors', 0),
            "addresses_processed": stats.get('addresses_processed', 0),
            "addresses_updated": stats.get('addresses_updated', 0),
            "addresses_skipped": stats.get('addresses_skipped', 0)
        }
    }))
except FileNotFoundError:
    print("Statistics file not found. Unable to report statistics.")
except json.JSONDecodeError:
    print("Error reading statistics file. Unable to report statistics.")
