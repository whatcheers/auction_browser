import os
import subprocess
import json

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(["python3", script_name], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode == 0

def aggregate_statistics():
    stats = {
        "auctions_scraped": 0,
        "items_added": 0,
        "items_updated": 0,
        "items_removed": 0,
        "items_skipped": 0,
        "errors": 0
    }

    stats_files = [
        'wisco_list_statistics.json',
        'wisco_extract_statistics.json',
        'wisco_mysql_statistics.json',
        'wisco_latlong_statistics.json'
    ]

    for file in stats_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                file_stats = json.load(f)
                for key in stats:
                    stats[key] += file_stats.get(key, 0)

    return stats

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    scripts = [
        "wisco-list-scrape.py",
        "wisco-scrape-extract.py",
        "wisco-scrape-mysql.py",
        "wisco-latlong.py"
    ]

    for script in scripts:
        success = run_script(script)
        if not success:
            print(f"Error running {script}")
            exit(1)

    # Aggregate and print statistics
    stats = aggregate_statistics()
    print("\nWisconsin Surplus Scraping Statistics:")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Output statistics in the format expected by the orchestrator
    print(json.dumps({"wisco-scrape.py": stats}))

    # Save aggregated statistics
    with open('wisconsinsurplus_statistics.json', 'w') as f:
        json.dump(stats, f)