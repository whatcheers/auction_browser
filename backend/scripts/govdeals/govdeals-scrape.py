import os
import subprocess

# Delete all HTML files in the current directory
html_files = [file for file in os.listdir('.') if file.endswith('.html')]
for file in html_files:
    os.remove(file)

# List of scripts to run
scripts = [
    "govdeals-scrape.js",
    "govdeals-extract.py",
    "govdeals-mysql.py",
    "govdeals-latlong.py",
    "./archive/govdeals-maint.py"
]

# Run each script
for script in scripts:
    if script.endswith('.js'):
        subprocess.run(["node", script])
    elif script.endswith('.py'):
        subprocess.run(["python3", script])