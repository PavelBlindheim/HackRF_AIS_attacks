import pycrc.algorithms
from CRC_generator import compute_crc # type: ignore

def octet_reverser(payload):
    reversedstring = ""
    for x in range(0, len(payload), 8):
        octet = payload[x:x+8]
        reversedstring += octet[::-1]

    return reversedstring


def bit_stuffer(data):
    stuffed_data = ""
    count = 0
    
    for index, bit in enumerate(data):
        if bit == '1':
            count += 1
        else:
            count = 0
            
        stuffed_data += bit
        
        if count == 5:
            stuffed_data += '0'
            count = 0

    return stuffed_data

def insert_flags_preamble_ramp_buffer(payload):
    packet = ""
    ramp = "00000000"
    preamble = "101010101010101010101010" 
    flag = "01111110" 
    packet += payload
    packet += flag
    packet = flag + packet
    packet = preamble + packet
    packet = ramp + packet
    packet = packet.ljust(256, '0')
    return packet


def nrzi_decode(nrzi_string):
    if not nrzi_string:
        return ''    
    result = []
    previous_signal = '0'
    result.append('1')
    
    for signal in nrzi_string[1:]:
        if signal == previous_signal:
            result.append('1')
        else:
            result.append('0')
        previous_signal = signal
    
    return ''.join(result)


def nrzi_encode(packet):
    signal = "0"
    nrzi_result = [""]
    for bit in packet:
        if bit == "0":
            if signal == "1": 
                signal = "0"
            else:
                signal =  "1"
        nrzi_result.append(signal)
    return ''.join(nrzi_result)


crc = pycrc.algorithms.Crc(width = 16, poly = 0x1021,
          reflect_in = False, xor_in = 0xFFFF,
          reflect_out = False, xor_out = 0xFFFF)


def assembler(AIS_data):
    CRC = compute_crc(AIS_data)
    payload = AIS_data+CRC
    reversed_payload = octet_reverser(payload)
    stuffed_payload = bit_stuffer(reversed_payload) 
    full_packet = insert_flags_preamble_ramp_buffer(stuffed_payload)
    nrzi_encoded_signal = nrzi_encode(full_packet)
    return nrzi_encoded_signal


def binary_string_to_bytes(binary_string):
    padded_length = (len(binary_string) + 7) // 8 * 8
    binary_string = binary_string.zfill(padded_length)
    byte_array = int(binary_string, 2).to_bytes(len(binary_string) // 8, byteorder='big')
    return byte_array
