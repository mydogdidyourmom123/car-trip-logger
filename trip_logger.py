import os
import csv
import serial
import time
import pynmea2
from datetime import datetime

# Serial port for GPS
SERIAL_PORT = '/dev/ttyACM0'  # your GPS device
BAUD_RATE = 9600

# Trips directory
TRIPS_DIR = os.path.expanduser("~/trip_web_app/trips/")
os.makedirs(TRIPS_DIR, exist_ok=True)

# Determine new trip number and filename
trip_number = len([f for f in os.listdir(TRIPS_DIR) if f.startswith("trip_")]) + 1
trip_filename = f"trip_{trip_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
trip_path = os.path.join(TRIPS_DIR, trip_filename)
print(f"Started new trip #{trip_number} -> {trip_path}")

# Open CSV file
with open(trip_path, 'w', newline='') as csvfile:
    fieldnames = ["Timestamp", "Latitude", "Longitude", "Altitude", "Speed"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        exit(1)

    print("Logger started, waiting for GPS fix...")
    gps_locked = False  # flag to check if we have a valid fix

    while True:
        line = ser.readline().decode('ascii', errors='replace').strip()
        if not line.startswith("$GPGGA") and not line.startswith("$GPRMC"):
            continue  # ignore non-location sentences

        try:
            msg = pynmea2.parse(line)

            # --- Check GPS fix ---
            if not gps_locked:
                if hasattr(msg, 'gps_qual') and int(msg.gps_qual) > 0:
                    gps_locked = True
                    print("GPS locked! Starting logging...")
                else:
                    continue  # skip logging until we have a fix

            # --- Log data after lock ---
            if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                lat = msg.latitude
                lon = msg.longitude
                alt = getattr(msg, 'altitude', 0.0)
                speed = getattr(msg, 'spd_over_grnd', 0.0)  # in knots
                timestamp = datetime.now().strftime("%H%M%S.%f")[:-3]

                writer.writerow({
                    "Timestamp": timestamp,
                    "Latitude": lat,
                    "Longitude": lon,
                    "Altitude": alt,
                    "Speed": speed
                })
                csvfile.flush()
                print(f"{timestamp}: {lat}, {lon}, Alt:{alt}, Spd:{speed}")

        except pynmea2.ParseError:
            continue
