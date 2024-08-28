import os
import subprocess
import sys

def run_script():
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
   
    # Construct the absolute path to smc-list.js
    smc_list_path = os.path.join(script_dir, "smc-list.js")
   
    # Run smc-list.js using Node.js
    process = subprocess.Popen(["node", smc_list_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        sys.stdout.write(line)
        # Check if the script outputs "No new auctions found. Exiting..." and exit early
        if "No new auctions found. Exiting..." in line:
            print("No new auctions found. Skipping further processing.")
            process.kill()
            sys.exit(0)
    for line in process.stderr:
        sys.stderr.write(line)
    process.wait()
       
    # Check the exit code
    if process.returncode != 0:
        print("Error running smc-list.js")
        sys.exit(1)

def run_additional_scripts():
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
   
    # Construct the absolute paths to the additional scripts
    smc_extract_path = os.path.join(script_dir, "smc-extract.py")
    smc_mysql_path = os.path.join(script_dir, "smc-mysql.py")
    smc_latlong_path = os.path.join(script_dir, "smc-latlong.py")
   
    # Run smc-extract.py using Python
    print("Running smc-extract.py...")
    result = subprocess.run(["python3", smc_extract_path], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        print(f"Error running smc-extract.py: {result.stderr}")
        sys.exit(1)

    # Run smc-mysql.py using Python
    print("Running smc-mysql.py...")
    result = subprocess.run(["python3", smc_mysql_path], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        print(f"Error running smc-mysql.py: {result.stderr}")
        sys.exit(1)
   
    # Run smc-latlong.py using Python
    print("Running smc-latlong.py...")
    result = subprocess.run(["python3", smc_latlong_path], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        print(f"Error running smc-latlong.py: {result.stderr}")
        sys.exit(1)

if __name__ == '__main__':
    run_script()
    run_additional_scripts()
