import os
import subprocess
import sys
import json

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(["python3", script_name], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode == 0

def run_node_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(["node", script_name], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode == 0, "No new auctions found" in result.stdout

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
        'smc_list_statistics.json',
        'smc_extract_statistics.json',
        'smc_mysql_statistics.json',
        'smc_latlong_statistics.json'
    ]

    for file in stats_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                file_stats = json.load(f)
                for key in stats:
                    if key in file_stats:
                        stats[key] += file_stats[key]

    return stats

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    scripts = [
        ("smc-list.js", run_node_script),
        ("smc-extract.py", run_script),
        ("smc-mysql.py", run_script),
        ("smc-latlong.py", run_script)
    ]

    for script, run_func in scripts:
        if script.endswith('.js'):
            success, no_new_auctions = run_func(script)
            if no_new_auctions:
                print("No new auctions found. Skipping further processing.")
                sys.exit(0)
        else:
            success = run_func(script)
        
        if not success:
            print(f"Error running {script}")
            sys.exit(1)

    # Aggregate and print statistics
    stats = aggregate_statistics()
    print("\nSMC Scraping Statistics:")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Output statistics in the format expected by the orchestrator
    print(json.dumps({"smc-scrape.py": stats}))