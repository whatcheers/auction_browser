import os
import sys
import subprocess

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(["python3", script_name], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        return False
    else:
        print(f"{script_name} completed successfully.")
        return True

# Run the proxibid-lot-scraper.js script (using Node.js)
lot_scraper_exit_code = os.system("node proxibid-lot-scraper.js")
if lot_scraper_exit_code != 0:
    print("Error occurred in proxibid-lot-scraper.js. Exiting the script.")
    sys.exit(1)

# Run the proxibid-import.py script
if not run_script("proxibid-import.py"):
    print("Error occurred in proxibid-import.py. Exiting the script.")
    sys.exit(1)

# Run the proxibid-latlong.py script
run_script("proxibid-latlong.py")

print("All Proxibid scripts have been executed.")