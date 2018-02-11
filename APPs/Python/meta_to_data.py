#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Meta To Data
# Generated: Sat Feb 10 12:53:13 2018
##################################################

import sys
import pmt
from gnuradio.blocks import parse_file_metadata
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import gr, blocks
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser

class meta_to_data(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Meta To Data")
        ##################################################
        # Variables
        ##################################################
        meta_file = "./Data/meta.raw"
        data_file = "./Data/data.raw"
        header_file = "./Data/header.txt"

        ##################################################
        # Blocks
        ##################################################
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, data_file, False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_file_meta_source_0 = blocks.file_meta_source(meta_file, True, False, '')

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_meta_source_0, 0), (self.blocks_file_sink_0, 0))

        ##################################################
        # Get header info
        ##################################################
        print "##################################################"
        print "#                 Header Info                    #"
        print "##################################################"

        handle = open(meta_file, "rb")
        hdr_start = handle.tell()
        header_str = handle.read(parse_file_metadata.HEADER_LENGTH)
        header = pmt.deserialize_str(header_str)
        info = parse_file_metadata.parse_header(header, True)
        if(info["extra_len"] > 0):
            extra_str = handle.read(info["extra_len"])
            extra = pmt.deserialize_str(extra_str)
        extra_info = parse_file_metadata.parse_extra_dict(extra, info, True)
        handle.close()

        header = open(header_file, "wb")
        rx_rate = extra_info['rx_rate']
        rx_freq = pmt.to_python(extra_info['rx_freq'])
        rx_time = extra_info['rx_time']
        header.write("%.00f\n"%rx_rate)
        header.write("%.00f\n"%rx_freq)
        header.write("%.22f\n"%rx_time)
        header.close()

        print


def main(top_block_cls=meta_to_data, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
    
