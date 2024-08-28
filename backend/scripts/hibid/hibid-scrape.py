import os
import shutil
import datetime

# Run the hibid-list-scrape.py script
os.system('python3 hibid-list-scrape.py')

# Run the hibid-list-mysql.py script
os.system('python3 hibid-list-mysql.py')

# Run the hibid-scrape-individual.py script
os.system('python3 hibid-scrape-individual.py')

# Move all .json files to the archive/ directory
for filename in os.listdir('.'):
    if filename.endswith('.json'):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        archive_path = os.path.join('archive', new_filename)
        if not os.path.exists(archive_path):
            shutil.move(filename, archive_path)
        else:
            print(f"File {filename} already exists in the archive directory, skipping.")

# Remove all .html files
for filename in os.listdir('.'):
    if filename.endswith('.html'):
        os.remove(filename)