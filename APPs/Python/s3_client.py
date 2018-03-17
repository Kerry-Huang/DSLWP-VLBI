import os
import pmt
import time
import math
import boto3
import urllib2
import threading
import ConfigParser
from gnuradio.blocks import parse_file_metadata

    
########config########
cp = ConfigParser.SafeConfigParser()
cp.read('./config.ini')

##cutter
rawfile_path = cp.get('cutter','rawfile_path')
package_path = cp.get('cutter','package_path')
timeapi_url = cp.get('cutter','timeapi_url')
package_prefix = cp.get('cutter','package_prefix')
package_amount = cp.getint('cutter','package_amount')
    
##s3
s3_url = cp.get('s3','s3_url')
access_key_id = cp.get('s3','access_key_id')
secret_access_key = cp.get('s3','secret_access_key')
######################

class S3_percentage(object):
    def __init__(self,uploadID,timestamp,file_fullpath):
        self.uploadID = uploadID
        self.timestamp = timestamp
        self.file_fullpath = file_fullpath
        self.size = float(os.path.getsize(file_fullpath))
        self.seen_so_far = 0
    def __call__(self, bytes_amount):
        self.seen_so_far += bytes_amount
        percentage = (self.seen_so_far / self.size) * 100
        print(
            "\033[%d;0H%15s %15d %15d  (%.2f%%)" % (
            self.uploadID + 14, self.timestamp, self.seen_so_far, self.size, percentage)
        )

class S3_uploadtask(threading.Thread):
    def __init__(self,threadID,timestamp,file_name,file_fullpath):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.timestamp = timestamp
        self.file_name = file_name
        self.file_fullpath = file_fullpath

    def run(self):
        s3 = boto3.resource(
            's3',
            endpoint_url = s3_url,
            aws_access_key_id = access_key_id,
            aws_secret_access_key = secret_access_key,
            config=boto3.session.Config(signature_version='s3v4')
        )

        s3.Bucket('vlbi').upload_file (
            self.file_fullpath,
            self.file_name,
            Callback=S3_percentage(self.threadID,self.timestamp,self.file_fullpath)
        )

def main():
    #init
    nread = 0
    old_timestamp = 0
    new_timestamp = 0
    uploadtaskID = 0
    
    os.system("clear")    
    #open the file
    handle = open(rawfile_path, "rb")
    handle.seek(nread, 0)
    hdr_start = handle.tell()

    #read the base header
    header_str = handle.read(parse_file_metadata.HEADER_LENGTH)
    header = pmt.deserialize_str(header_str)
    init_info = parse_file_metadata.parse_header(header, True)
    handle.close()


    package_length = parse_file_metadata.HEADER_LENGTH + init_info["extra_len"] + init_info['nbytes']


    while (True):
        timeapi = urllib2.urlopen(timeapi_url)
        new_timestamp = int(timeapi.read())
        if (old_timestamp != new_timestamp):

            if (int(math.floor(new_timestamp)) >= int(math.ceil(init_info['rx_time']))):

                delta_time = int(math.floor(new_timestamp)) - int(math.ceil(init_info['rx_time']))
                if (((delta_time + package_amount) * package_length) <= os.path.getsize(rawfile_path)):

                    nread = delta_time * package_length
                    handle = open(rawfile_path, "rb")
                    handle.seek(nread, 0)
                    hdr_start = handle.tell()
                    package_str = handle.read(package_amount * package_length)
                    handle.close()

                    #create package file
                    package_name = package_prefix + "_{0}.raw".format(new_timestamp)
                    package_fullpath = package_path + package_name
                    package = open(package_fullpath, "wb")
                    package.write(package_str)
                    package.close()

                    print "\033[13;0H%15s %15s %15s" %("|   Timestamp|","|Upload_Bytes|","|   All_Bytes|")

                    uploadtask = S3_uploadtask(uploadtaskID,new_timestamp,package_name,package_fullpath)
                    uploadtask.setDaemon(True)
                    uploadtask.start()
                    uploadtaskID += 1
                    old_timestamp = new_timestamp
        time.sleep(5)

if __name__ == "__main__":
    main()
