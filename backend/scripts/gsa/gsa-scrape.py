import subprocess

subprocess.run(["node", "GSA-list.js"])
subprocess.run(["python3", "GSA-mysql.py"])
subprocess.run(["python3", "GSA-latlong.py"])
subprocess.run(["python3", "GSA-maint.py"])