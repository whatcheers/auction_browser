#!/bin/bash
# Load the user's profile
source /home/whatcheer/.bashrc  # Use .bashrc or .profile depending on your setup

# Activate the virtual environment
source ~/auction_browser/venv/bin/activate

# Navigate to the script directory
cd ~/auction_browser/backend/scripts

# Execute the Python script
python3 automate-scrape.py

# Deactivate the virtual environment
deactivate
