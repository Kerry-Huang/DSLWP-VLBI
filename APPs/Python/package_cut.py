import os
import pmt
import time
import math
from gnuradio.blocks import parse_file_metadata

##################################################
# Variables
##################################################
filename = "./Data/meta.raw"
subname = "package"
data_length = 2000000


def main(filename):

    #init
    nheaders = 0
    nread = 0
    
    while (True):

        #open the file
        handle = open(filename, "rb")
        handle.seek(nread, 0)
        hdr_start = handle.tell()

        #read the base header
        header_str = handle.read(parse_file_metadata.HEADER_LENGTH)
        header = pmt.deserialize_str(header_str)
        print "Package {0} Header".format(nheaders)
        info = parse_file_metadata.parse_header(header, True)

        #read the extra header
        if(info["extra_len"] > 0):
            extra_str = handle.read(info["extra_len"])
            if(len(extra_str) == 0):
                break
            extra = pmt.deserialize_str(extra_str)
            extra_info = parse_file_metadata.parse_extra_dict(extra, info, True)

        #read the data
        data_str = handle.read(info['nbytes'])

        #prepare for next package
        if (info['nbytes'] != 0):
            nheaders += 1
            nread += parse_file_metadata.HEADER_LENGTH + info["extra_len"] + info['nbytes']
        handle.close()

        #create package file
        package_name = "Package_{0}.raw".format(int(math.ceil(info['rx_time'])))
        package_path = "./Data/package/"+package_name
        package = open(package_path, "wb")
        package.write(header_str)
        package.write(extra_str)
        package.write(data_str)
        package.close()


        while (True):
            size = os.path.getsize(filename)
            if (parse_file_metadata.HEADER_LENGTH + info["extra_len"] + data_length < size - nread):
                break
            time.sleep(0.5)
        os.system("clear")


if __name__ == "__main__":
    main(filename)
