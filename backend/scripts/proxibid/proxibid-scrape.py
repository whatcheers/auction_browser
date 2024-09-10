import subprocess
import json
import os

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(["python3", script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        return False
    return True

def run_node_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(["node", script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        return False
    return True

def aggregate_statistics(stats_files):
    aggregated_stats = {
        "auctions_scraped": 0,
        "items_added": 0,
        "items_updated": 0,
        "items_removed": 0,
        "items_skipped": 0,
        "errors": 0,
        "addresses_processed": 0,
        "addresses_updated": 0,
        "addresses_skipped": 0
    }

    for stats_file in stats_files:
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                stats = json.load(f)
                for key in aggregated_stats:
                    aggregated_stats[key] += stats.get(key, 0) or 0  # Ensure None values are treated as 0

    return aggregated_stats

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    scripts = [
        ("proxibid-lot-scraper.js", run_node_script),
        ("proxibid-import.py", run_script),
        ("proxibid-latlong.py", run_script)
    ]

    for script, run_function in scripts:
        success = run_function(script)
        if not success:
            print(f"Error occurred while running {script}. Exiting.")
            exit(1)

    stats_files = [
        'proxibid_statistics.json'
    ]

    # Aggregate and print statistics
    aggregated_stats = aggregate_statistics(stats_files)
    print("\nProxibid Scraping Statistics:")
    for key, value in aggregated_stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Save aggregated statistics
    with open('proxibid_statistics.json', 'w') as f:
        json.dump(aggregated_stats, f, indent=2)

    # Output statistics in the format expected by the orchestrator
    print(json.dumps({"proxibid-scrape.py": aggregated_stats}))