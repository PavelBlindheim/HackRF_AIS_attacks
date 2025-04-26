import time
from flask import Flask, render_template, request
import subprocess
from pyais.encode import encode_dict
from AIS_constructor import assembler

app = Flask(__name__)

# Sample AIS signal data structure for encoding
data = {
    'msg_type': 1,
    'course': 220.3,
    'lat': 0.0,  # To be updated with actual latitude
    'lon': 0.0,  # To be updated with actual longitude
    'mmsi': '666',
    'turn': 127.0,
    'speed': 0.9,
    'heading': 23,
    'second': 4,
}

# Simplified, not taking into account changing course
def set_reporting_interval(speed_knots):
    if speed_knots <= 3:
        return 180 if speed_knots == 0 else 10  # 3 minutes if anchored, 10 seconds if moving up to 3 knots
    elif 3 < speed_knots <= 14:
        return 10  # 10 seconds for speeds between 3 and 14 knots
    elif speed_knots > 14:
        return 2  

import geopy.distance
import math

def calculate_course(lat1, lon1, lat2, lon2, prev_course=None):
    """Calculate the course (COG) between two lat/lon points, avoiding 0.0 course."""
    delta_lon = math.radians(lon2 - lon1)
    lat1, lat2 = map(math.radians, [lat1, lat2])
    
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    course = (initial_bearing + 360) % 360
    
    if course == 0.0 and prev_course is not None:
        return prev_course  # Use the previous course to prevent breaking changes
    
    return course

def interpolate_positions(start, end, speed_knots, interval):
    """Generate intermediate positions based on speed and interval."""
    distance = geopy.distance.geodesic(start, end).nm  # Convert to nautical miles
    time_needed = distance / float(speed_knots) * 3600  # Time in seconds
    num_points = max(1, int(time_needed / interval))  # Number of reports needed
    
    lat1, lon1 = start
    lat2, lon2 = end
    
    positions = [(lat1, lon1)]
    for i in range(1, num_points):
        fraction = i / num_points
        lat = lat1 + fraction * (lat2 - lat1)
        lon = lon1 + fraction * (lon2 - lon1)
        positions.append((lat, lon))
    
    positions.append((lat2, lon2))  # Ensure the final point is included
    return positions

def generate_strings(coords, speed, mmsi, reporting_interval):
    """Generate AIS messages with realistic course and interpolated positions."""
    all_signals = []
    all_data = []
    interval = reporting_interval
    prev_point = None
    prev_course = None
    second_counter = 0
    
    for point in coords:
        point = point[::-1]
        if prev_point:
            interpolated_points = interpolate_positions(prev_point, point, speed, interval)
            for lat, lon in interpolated_points:
                course = calculate_course(prev_point[0], prev_point[1], lat, lon, prev_course)
                prev_course = course                
                data = {
                    'msg_type': 1,
                    'course': round(course, 1),
                    'lat': lat,
                    'lon': lon,
                    'mmsi': mmsi,
                    'turn': 127.0,
                    'speed': speed,
                    'heading': int(course),
                    'second': second_counter,
                }
                all_data.append(data)
                second_counter += interval
        prev_point = point

    for data in all_data:
        signal = encode_dict(data, radio_channel="A", talker_id="AIVDM")[0]
        all_signals.append(signal)

    
    return all_signals


def ascii_to_6bit_binary(ascii_string):
    ascii_table = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
        '8': 8, '9': 9, ':': 10, ';': 11, '<': 12, '=': 13, '>': 14, '?': 15,
        '@': 16, 'A': 17, 'B': 18, 'C': 19, 'D': 20, 'E': 21, 'F': 22, 'G': 23,
        'H': 24, 'I': 25, 'J': 26, 'K': 27, 'L': 28, 'M': 29, 'N': 30, 'O': 31,
        'P': 32, 'Q': 33, 'R': 34, 'S': 35, 'T': 36, 'U': 37, 'V': 38, 'W': 39,
        '`': 40, 'a': 41, 'b': 42, 'c': 43, 'd': 44, 'e': 45, 'f': 46, 'g': 47,
        'h': 48, 'i': 49, 'j': 50, 'k': 51, 'l': 52, 'm': 53, 'n': 54, 'o': 55,
        'p': 56, 'q': 57, 'r': 58, 's': 59, 't': 60, 'u': 61, 'v': 62, 'w': 63
    }
    binary_string = ''.join(format(ascii_table[char], '06b') for char in ascii_string)
    return binary_string

def generate_full_string(coords, speed, mmsi, reporting_interval):
    strings = generate_strings(coords, speed, mmsi, reporting_interval)
    strings = [message.split(',')[5] for message in strings]
    final = []
    for x in strings:
        bits = ascii_to_6bit_binary(x)
        ais_signal = assembler(bits)
        final.append(ais_signal)
        # final += "0" * 128  # Adding 0's to make some space between the signals
    return final
    

def realistic_sender(coordinates, speed, mmsi, hackrf):
    expected_interval = set_reporting_interval(float(speed))
    signals = generate_full_string(coordinates, speed, mmsi, expected_interval)
    for signal in signals:
        result = subprocess.run(
            ['python3.12', 'transmitter.py', signal, hackrf],
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress standard output
        )
        time.sleep(expected_interval)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coordinates', methods=['POST'])
def receive_coordinates():
    data = request.json
    coords = data['coordinates']
    speed = data['speed']
    mmsi = data['mmsi']
    print("Received coordinates:", coords)
    print("Received coordinates:", speed)
    print("Received coordinates:", mmsi)
    realistic_sender(coords, speed, mmsi, "0000000000000000f75461dc293aa3c3")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=5001)
