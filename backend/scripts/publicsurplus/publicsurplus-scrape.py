import os
import sys

# Run the publicsurplus-newitems.py script
newitems_exit_code = os.system("python3 publicsurplus-newitems.py")
if newitems_exit_code != 0:
    print("No new auctions found. Exiting the script.")
    sys.exit(0)

# Run the publicsurplus-latlong.py script
os.system("python3 publicsurplus-mysql.py")

# Run the publicsurplus-mysql.py script
os.system("python3 publicsurplus-latlong.py")
