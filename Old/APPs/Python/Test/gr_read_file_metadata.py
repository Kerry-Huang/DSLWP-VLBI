#!/usr/bin/env python
#
# Copyright 2012 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import sys
from optparse import OptionParser

import pmt
from gnuradio.blocks import parse_file_metadata

def main(filename, detached=False):
    handle = open(filename, "rb")

    nheaders = 0
    nread = 0
    while(True):
        # read out next header bytes
        hdr_start = handle.tell()
        header_str = handle.read(parse_file_metadata.HEADER_LENGTH)
        if(len(header_str) == 0):
            break

        # Convert from string to PMT (should be a dictionary)
        try:
            header = pmt.deserialize_str(header_str)
        except RuntimeError:
            sys.stderr.write("Could not deserialize header: invalid or corrupt data file.\n")
            sys.exit(1)

        print "HEADER {0}".format(nheaders)
        info = parse_file_metadata.parse_header(header, True)
        print "%.22f" %(info["rx_time"])

        if(info["extra_len"] > 0):
            extra_str = handle.read(info["extra_len"])
            if(len(extra_str) == 0):
                break

            try:
                extra = pmt.deserialize_str(extra_str)
            except RuntimeError:
                sys.stderr.write("Could not deserialize extras: invalid or corrupt data file.\n")
                sys.exit(1)

            print "\nExtra Header:"
            extra_info = parse_file_metadata.parse_extra_dict(extra, info, True)

        nheaders += 1
        nread += parse_file_metadata.HEADER_LENGTH + info["extra_len"]
        if(not detached):
            nread += info['nbytes']
        handle.seek(nread, 0)
        print "\n\n"

if __name__ == "__main__":
    usage="%prog: [options] filename"
    description = "Read in a GNU Radio file with meta data, extracts the header and prints it."

    parser = OptionParser(conflict_handler="resolve",
                          usage=usage, description=description)
    parser.add_option("-D", "--detached", action="store_true", default=False,
                      help="Used if header is detached.")
    (options, args) = parser.parse_args ()

    if(len(args) < 1):
        sys.stderr.write("No filename given\n")
        sys.exit(1)

    filename = args[0]
    main(filename, options.detached)
