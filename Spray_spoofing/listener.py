import subprocess
from pyais import decode
import sys

# Retrieve target_mmsi from command-line arguments
if len(sys.argv) < 2:
    print("Error: target_mmsi argument missing", file=sys.stderr)
    sys.exit(1)
target_mmsi = sys.argv[1]

# Set up AIS catcher command
AIS_catcher_filepath = "/usr/bin/AIS-catcher"
args = ["-v", "10", "-d", "0000000000000000675c62dc30630dcf"]
command = [AIS_catcher_filepath] + args

# Open the subprocess
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def data_processor(line):
    # Process the line as needed
    if line[0] != "!":
        return  # Skip lines that are not AIS messages
    
    # Parse AIS message from the line
    received_signal = line[:line.find('*') + 3]
    bin_version = received_signal.encode('utf-8')
    
    try:
        decoded = decode(bin_version)
    except Exception as e:
        print("Error decoding message:", e, file=sys.stderr)
        return  # Skip to the next line if decoding fails
    
    # Check if the MMSI in decoded message matches the target MMSI
    if str(decoded.mmsi) == target_mmsi:
        print(bin_version)  # Send the decoded message to stdout
        process.terminate()  # Exit after finding the target MMSI

# Continuously read the subprocess output
while True:
    line = process.stdout.readline()
    
    if not line:
        break  # Exit if no more lines are available
    
    data_processor(line)

# Process any remaining buffered stderr output (if needed)
remaining_stderr = process.stderr.read()
if remaining_stderr:
    print("STDERR:", remaining_stderr, file=sys.stderr)
