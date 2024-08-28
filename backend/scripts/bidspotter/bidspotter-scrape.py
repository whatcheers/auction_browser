import subprocess

subprocess.run(["node", "bidspotter-list.js"])
subprocess.run(["python3", "bidspotter-mysql.py"])
subprocess.run(["python3", "bidspotter-latlong.py"])
