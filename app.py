import os
import csv
from flask import Flask, render_template

app = Flask(__name__)

TRIPS_DIR = os.path.expanduser("~/trip_web_app/trips/")

@app.route("/")
def index():
    trips = []
    files = sorted(os.listdir(TRIPS_DIR))
    for file in files:
        if file.endswith(".csv"):
            trip_coords = []
            with open(os.path.join(TRIPS_DIR, file), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        lat = float(row["Latitude"])
                        lon = float(row["Longitude"])
                        trip_coords.append({"lat": lat, "lon": lon})
                    except ValueError:
                        continue
            trips.append({"file": file, "coords": trip_coords})
    return render_template("index.html", trips=trips)
