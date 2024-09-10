import subprocess
import json
import os

def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {command[0]}:")
        print(result.stderr)
        return False
    return True

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize statistics
stats = {
    "auctions_scraped": 0,
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0
}

# Run the scraping and processing scripts
scripts = [
    ["node", os.path.join(current_dir, "govdeals-scrape.js")],
    ["python3", os.path.join(current_dir, "govdeals-extract.py")],
    ["python3", os.path.join(current_dir, "govdeals-mysql.py")],
    ["python3", os.path.join(current_dir, "govdeals-latlong.py")],
    ["python3", os.path.join(current_dir, "archive", "govdeals-maint.py")]
]

for script in scripts:
    success = run_command(script)
    if not success:
        stats["errors"] += 1

# Read and merge statistics from each script
for filename in ['govdeals_statistics.json', 'govdeals_statistics.json']:
    try:
        with open(os.path.join(current_dir, filename), 'r') as f:
            file_stats = json.load(f)
            for key in stats:
                if key in file_stats:
                    stats[key] += file_stats[key]
    except FileNotFoundError:
        print(f"Statistics file {filename} not found.")
    except json.JSONDecodeError:
        print(f"Error reading statistics file {filename}.")

# Map old keys to new keys if necessary
if "items_errored" in stats:
    stats["errors"] += stats.pop("items_errored")

print("\nGovDeals Scraping Statistics:")
for key, value in stats.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

# Output statistics in the format expected by the orchestrator
print(json.dumps({"govdeals-scrape.py": stats}))

# Save the final statistics
with open(os.path.join(current_dir, 'govdeals_statistics.json'), 'w') as f:
    json.dump(stats, f, indent=2)