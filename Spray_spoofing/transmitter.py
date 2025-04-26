import sys
import signal
import argparse
from gnuradio import blocks, digital, gr
import pmt
from gnuradio.filter import firdes
from gnuradio.fft import window
import osmosdr


class top_block(gr.top_block):
    def __init__(self, byte_list, hackrf_id):
        gr.top_block.__init__(self, "Example AIS Transmitter", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = 8e6
        self.bit_rate = 9600

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + f'hackrf={hackrf_id}'
        )
        self.osmosdr_sink_0.set_sample_rate(self.samp_rate)
        # self.osmosdr_sink_0.set_center_freq(161975000, 0) ### This should be used if the attacker has a license to transmit on AIS frequency
        self.osmosdr_sink_0.set_center_freq(433000000, 0) 
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(10, 0)
        self.osmosdr_sink_0.set_if_gain(0, 0)
        self.osmosdr_sink_0.set_bb_gain(0, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.digital_gmsk_mod_0 = digital.gmsk_mod(
            samples_per_symbol=(int(self.samp_rate / self.bit_rate)),
            bt=0.4,
            verbose=False,
            log=False,
            do_unpack=True
        )
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_cc(0.9, 1)

        # Replace file_source with vector_source_b using the byte_list
        self.blocks_vector_source_0 = blocks.vector_source_b(byte_list, False, 1)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_vector_source_0, 0), (self.digital_gmsk_mod_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.digital_gmsk_mod_0, 0), (self.blocks_multiply_const_xx_0, 0))

def bits_to_bytes(bits):
    return [sum([bits[i + j] << (7 - j) for j in range(8)]) for i in range(0, len(bits), 8)]


def main(bit_string, hackrf_id, top_block_cls=top_block, options=None):
    print(bit_string)
    bit_list = [int(bit) for bit in bit_string if bit in '01']
    byte_list = bits_to_bytes(bit_list)
    print(byte_list)
    print("!!!!!1", hackrf_id)
    tb = top_block_cls(byte_list, hackrf_id)
    print(tb)
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Example AIS Transmitter")
    parser.add_argument('byte_string', type=str, help='Byte string to be transmitted')
    parser.add_argument('hackrf_id', type=str, help='HackRF device ID')
    args = parser.parse_args()
    main(args.byte_string, args.hackrf_id)

