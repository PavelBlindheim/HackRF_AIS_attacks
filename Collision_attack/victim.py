import subprocess
import time
from pyais.encode import encode_dict
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





start = [10.739573904759887, 59.9307262443234]
end = [10.774940031007993, 59.92952207732171]
speed_knots = 25  # Example speed in knots
mmsi = "333"

signals = generate_coordinates(start, end, speed_knots, mmsi)

strings = generate_strings(signals)
all_strings = generate_full_string(strings)

realistic_sender(all_strings, "0000000000000000675c62dc344672cf")
