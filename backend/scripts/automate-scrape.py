#!/usr/bin/env python3
import os
import sys
import subprocess
import configparser
import logging
import logging.handlers
import json
from datetime import datetime
import pytz

# Path for the log file using expanduser to correctly handle the '~'
log_file_path = os.path.expanduser('~/auction_browser/backend/automate-scrape.log')

# Set up logging with log rotation and timestamps
log_handler = logging.handlers.RotatingFileHandler(
    log_file_path,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5  # keep 5 backups
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

def log_event(level, message, **kwargs):
    event = {
        'level': level,
        'message': message,
        'timestamp': datetime.now(pytz.timezone('America/Chicago')).isoformat(),
    }
    event.update(kwargs)
    logging.log(level, json.dumps(event))

def print_colored(message, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'reset': '\033[0m'
    }
    print(f"{colors[color]}{message}{colors['reset']}")
    log_event(logging.INFO if color == 'green' else logging.ERROR if color == 'red' else logging.ERROR, message)

# Function to save last run status
def save_status(status, details=""):
    status_file = os.path.expanduser('~/auction_browser/backend/last_run_status.json')
    with open(status_file, 'w') as file:
        json.dump({
            'status': status,
            'timestamp': datetime.now(pytz.timezone('America/Chicago')).isoformat(),
            'details': details
        }, file)

# Get the current time in Chicago time zone
current_time = datetime.now(pytz.timezone('America/Chicago')).strftime('%Y-%m-%d %H:%M:%S')
print_colored(f"Current Chicago time: {current_time}", 'yellow')

# Change to the scripts directory
os.chdir(os.path.dirname(__file__))

# Dynamically find the config file relative to the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(script_dir, 'db.cfg')

print_colored(f"Attempting to read config file: {config_file}", 'yellow')

# Load MySQL connection details from config file
config = configparser.ConfigParser()

if not os.path.exists(config_file):
    print_colored(f"Config file not found: {config_file}", 'red')
    save_status("failed", f"Config file not found: {config_file}")
    exit(1)

config.read(config_file)

print_colored(f"Sections in config file: {config.sections()}", 'yellow')

if 'mysql' not in config.sections():
    print_colored("'mysql' section not found in the config file", 'red')
    save_status("failed", "'mysql' section not found in the config file")
    exit(1)

try:
    host = config.get('mysql', 'host')
    user = config.get('mysql', 'user')
    password = config.get('mysql', 'password')
    print_colored(f"Using MySQL connection details: host={host}, user={user}", 'green')
except configparser.NoOptionError as e:
    print_colored(f"Missing option in config file: {str(e)}", 'red')
    save_status("failed", f"Missing option in config file: {str(e)}")
    exit(1)

# Use sys.executable for the currently running Python interpreter in the virtual environment
venv_python = sys.executable

# Run the prep-env.py script using the virtual environment's Python
try:
    subprocess.run([venv_python, "prep-env.py"], check=True)
    print_colored("Successfully ran prep-env.py", 'green')
except subprocess.CalledProcessError as e:
    print_colored("An error occurred while running prep-env.py. Stopping the orchestrator.", 'red')
    save_status("failed", str(e))
    exit(1)

# Dictionary of directories and their respective scripts
directories_scripts = {
    "backes": ["backes-scrape.py"],
    "bidspotter": ["bidspotter-scrape.py"],
    "govdeals": ["govdeals-scrape.py"],
    "gsa": ["gsa-scrape.py"],
    "hibid": ["hibid-scrape.py"],
    "publicsurplus": ["publicsurplus-scrape.py"],
    "smc": ["smc-scrape.py"],
    "wisconsonsurplus": ["wisco-scrape.py"],
    "proxibid": ["proxibid-scrape.py"]
}

# Dictionary to store statistics for each script
script_statistics = {}

# Add this function after the existing functions
def aggregate_scraper_statistics(script_name):
    stats_file = f"{script_name.replace('-scrape.py', '')}_statistics.json"
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            stats = json.load(f)
            return {
                "auctions_scraped": stats.get("auctions_scraped", 0),
                "items_added": stats.get("items_added", 0),
                "items_updated": stats.get("items_updated", 0),
                "items_removed": stats.get("items_removed", 0),
                "items_skipped": stats.get("items_skipped", 0),
                "errors": stats.get("errors", 0)
            }
    return {}

# Replace the existing script execution loop with this:
for directory, scripts in directories_scripts.items():
    os.chdir(os.path.join(os.path.dirname(__file__), directory))
    for script in scripts:
        try:
            result = subprocess.run([venv_python, script], check=True, capture_output=True, text=True)
            print_colored(f"Successfully ran {script} in {directory}", 'green')
            
            # Aggregate statistics
            stats = aggregate_scraper_statistics(script)
            script_statistics[script] = stats
        except subprocess.CalledProcessError as e:
            print_colored(f"An error occurred while running {script} in {directory}. Stopping the orchestrator.", 'red')
            save_status("failed", str(e))
            exit(1)

# After the loop, add this code to print overall statistics
print_colored("\nOverall Scraping Statistics:", 'green')
overall_stats = {
    "auctions_scraped": 0,
    "items_added": 0,
    "items_updated": 0,
    "items_removed": 0,
    "items_skipped": 0,
    "errors": 0
}

for script, stats in script_statistics.items():
    print_colored(f"\n{script} Statistics:", 'yellow')
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
        if key in overall_stats:
            overall_stats[key] += value

print_colored("\nAggregate Statistics:", 'green')
for key, value in overall_stats.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

# Save the overall statistics
with open('overall_statistics.json', 'w') as f:
    json.dump(overall_stats, f, indent=2)