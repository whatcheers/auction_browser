0#!/bin/bash

# Check if exactly one argument is provided
if [ $# -ne 1 ]; then
  echo "Enter Auction Number Ex. "55""
  exit 1
fi

# Check if the argument is an integer
if ! [[ $1 =~ ^-?[0-9]+$ ]]; then
  echo "Error: Argument must be an integer."
  exit 1
fi

# Pass the argument to the Node.js script
node heartland-ingest.js "$1"

# Run the Python script without passing the integer argument
python3 heartland-process-titles.py

# Import into mysql

python3 heartland-mysql.py

# Update Summary with OpenAI
python3 call-mothership.py
mv response.txt ../response.html
