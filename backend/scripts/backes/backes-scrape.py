import subprocess

subprocess.run(["node", "backes-list.js"])
subprocess.run(["python3", "backes-extract.py"])
subprocess.run(["python3", "backes-mysql.py"])
subprocess.run(["python3", "backes-latlong.py"])
subprocess.run(["python3", "backes-maint.py"])
