import os
import csv
from flask import Flask, render_template

app = Flask(__name__)  # <-- this must come BEFORE any @app.route

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
                    lat_val = row.get("Latitude")
                    lon_val = row.get("Longitude")
                    if lat_val and lon_val:
                        try:
                            lat = float(lat_val)
                            lon = float(lon_val)
                            trip_coords.append({"lat": lat, "lon": lon})
                        except ValueError:
                            continue
            if trip_coords:  # skip trips with no valid points
                trips.append({"file": file, "coords": trip_coords})
    return render_template("index.html", trips=trips)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
