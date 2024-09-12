#!/bin/bash

# Set the path to your virtual environment
VENV_PATH="/home/whatcheer/auction_browser/venv"

# Set the path to your project directory
PROJECT_PATH="/home/whatcheer/auction_browser"

# Activate the virtual environment
. $VENV_PATH/bin/activate

# Set PATH to include the virtual environment's bin directory
export PATH="$VENV_PATH/bin:$PATH"

# Navigate to the script directory
cd $PROJECT_PATH/backend/scripts

# Ensure mysql-connector-python is installed
pip install mysql-connector-python

# Execute the Python script
python3 automate-scrape.py

# Run the parse_statistics.py script
python3 parse_statistics.py

# Deactivate the virtual environment
deactivate