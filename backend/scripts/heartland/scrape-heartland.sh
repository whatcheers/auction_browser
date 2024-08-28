#!/bin/bash

# Check if exactly one argument is provided
if [ $# -ne 1 ]; then
  echo "Enter Auction Number Ex. \"55\""
  exit 1
fi

# Check if the argument is an integer
if ! [[ $1 =~ ^-?[0-9]+$ ]]; then
  echo "Error: Argument must be an integer."
  exit 1
fi

# Pass the argument to the Node.js script
echo "Running heartland-ingest.js with auction number $1"
node heartland-ingest.js "$1"
if [ $? -ne 0 ]; then
  echo "heartland-ingest.js failed"
  exit 1
fi

# Run the Python script without passing the integer argument
echo "Running heartland-process-titles.py"
python3 heartland-process-titles.py
if [ $? -ne 0 ]; then
  echo "heartland-process-titles.py failed"
  exit 1
fi

# Import into mysql
echo "Running heartland-mysql.py"
python3 heartland-mysql.py
if [ $? -ne 0 ]; then
  echo "heartland-mysql.py failed"
  exit 1
fi

echo "All scripts ran successfully"
