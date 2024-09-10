import os
import sys
import json

def run_script(script_name):
    result = os.system(f"python3 {script_name}")
    if result != 0:
        print(f"Error running {script_name}. Exiting.")
        sys.exit(1)

# Run the individual scripts
run_script("publicsurplus-newitems.py")
run_script("publicsurplus-mysql.py")
run_script("publicsurplus-latlong.py")

# Aggregate statistics
stats_files = [
    'publicsurplus_newitems_statistics.json',
    'publicsurplus_mysql_statistics.json',
    'publicsurplus_latlong_statistics.json'
]

aggregated_stats = {
    "auctions_scraped": 0,
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0
}

for stats_file in stats_files:
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
            for key in aggregated_stats:
                aggregated_stats[key] += stats.get(key, 0)

# Save aggregated statistics
with open('publicsurplus_statistics.json', 'w') as f:
    json.dump(aggregated_stats, f, indent=2)

# Print aggregated statistics
print("\nPublic Surplus Scraping Statistics:")
for key, value in aggregated_stats.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

# Output statistics in the format expected by the orchestrator
print(json.dumps({"publicsurplus-scrape.py": aggregated_stats}))
