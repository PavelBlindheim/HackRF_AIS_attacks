import subprocess
from pyais import decode
import time

start_time = time.time()

AIS_catcher_filepath = "/usr/bin/AIS-catcher"

args = ["-N", "8100", "-v", "10", "-d", "0000000000000000675c62dc30630dcf"]

command = [AIS_catcher_filepath] + args

process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def data_processor(line):
    if line[0] != "!":
        print(line)
        return
    recieved_signal = line[:line.find('*') + 3]
    bin_version = recieved_signal.encode('utf-8')
    decoded = decode(bin_version)
    print(decoded.speed, f"{time.monotonic():.3f}")  

while True:
    line = process.stdout.readline()
    
    if line == '':
        break
    
    data_processor(line)

remaining_stderr = process.stderr.read()
if remaining_stderr:
    data_processor(remaining_stderr)
