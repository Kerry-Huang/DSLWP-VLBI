import os
import pmt
import time
import math
import boto3
import urllib2
import threading
import ConfigParser
from gnuradio.blocks import parse_file_metadata

################ Mark ################
INFO = "[\033[32mINFO\033[0m]"
ERROR = "[\033[31mERROR\033[0m]"
SUCCESS = "[\033[32mSUEECSS\033[0m]"
WARNING = "[\033[33mWARNING\033[0m]"
######################################

############### Config ###############
cp = ConfigParser.SafeConfigParser()
cp.read('./config.ini')
######################################

class S3_percentage(object):
	#Init var
	def __init__(self,uploadID,timestamp,file_fullpath):
		self.uploadID = uploadID
		self.timestamp = timestamp
		self.file_fullpath = file_fullpath
		self.size = float(os.path.getsize(file_fullpath))
		self.seen_so_far = 0

	#Callback upload percentage
	def __call__(self, bytes_amount):
		self.seen_so_far += bytes_amount
		percentage = (self.seen_so_far / self.size) * 100
		print(
			"\033[%d;0H%15s %15d %15d  (%.2f%%)" 
			% (self.uploadID + 22, self.timestamp, self.seen_so_far, self.size, percentage)
		)

class S3_uploadtask(threading.Thread):
	#Init var
	def __init__(self,config,threadID,timestamp,file_name,file_fullpath):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.timestamp = timestamp
		self.file_name = file_name
		self.file_fullpath = file_fullpath
		self.config = config
		##s3
		self.s3_url = self.config.get('s3','s3_url')
		self.access_key_id = self.config.get('s3','access_key_id')
		self.secret_access_key = self.config.get('s3','secret_access_key')
	
	#Upload thread
	def run(self):
		#Init upload connect
		s3 = boto3.resource(
				's3',
				endpoint_url = self.s3_url,
				aws_access_key_id = self.access_key_id,
				aws_secret_access_key = self.secret_access_key,
				config=boto3.session.Config(signature_version='s3v4')
			)
		try:
			#Begin upload
			s3.Bucket('vlbi').upload_file (
				self.file_fullpath,
				self.file_name,
				#Callback upload percentage
				Callback=S3_percentage(self.threadID,self.timestamp,self.file_fullpath)
			)
		except Exception as e:
			#return error
			print(
				"\033[%d;0H%15s  %s"
				% (self.threadID + 14, self.timestamp, e)
			)

class cutter:
	def __init__(self,config):
		#init var
		self.nread = 0
		self.old_timestamp = 0
		self.new_timestamp = 0
		self.uploadtaskID = 0
		#Get the config from config.ini
		self.config = config
		##cutter
		self.rawfile_path = self.config.get('cutter','rawfile_path')
		self.package_path = self.config.get('cutter','package_path')
		self.timeapi_url = self.config.get('cutter','timeapi_url')
		self.package_prefix = self.config.get('cutter','package_prefix')
		self.package_amount = self.config.getint('cutter','package_amount')	
		#Init screen
		os.system("clear")

	def get_timestamp(self):
		#open the file
		try:
			self.timeapi = urllib2.urlopen(self.timeapi_url)
			self.new_timestamp = int(self.timeapi.read())
		except Exception as e:
			print "\033[0;0H",ERROR,e
		else:
			print "\033[0;0H",INFO,"Server Timestamp:",self.new_timestamp

	def get_length(self):
		self.handle = open(self.rawfile_path, "rb")
		self.handle.seek(self.nread, 0)
		self.hdr_start = self.handle.tell()
		#read the base header
		self.header_str = self.handle.read(parse_file_metadata.HEADER_LENGTH)
		print "\033[1;0H"
		self.header = pmt.deserialize_str(self.header_str)
		self.init_info = parse_file_metadata.parse_header(self.header, True)
		self.handle.seek(0, 0)
		#get package_length
		self.package_length = parse_file_metadata.HEADER_LENGTH + self.init_info["extra_len"] + self.init_info['nbytes']
		self.info = self.init_info

	def find_package(self):
		while ((int(math.floor(self.new_timestamp)) - int(math.ceil(self.info['rx_time']))) > 0):
			# read out next header bytes
			self.hdr_start = self.handle.tell()
			self.header_str = self.handle.read(parse_file_metadata.HEADER_LENGTH)
			if(len(self.header_str) == 0):
				break
			# Convert from string to PMT (should be a dictionary)
			try:
				print "\033[1;0H"
				self.header = pmt.deserialize_str(self.header_str)
			except Exception as e:
				print ERROR,e
			else:
				print SUCCESS,"Found base header."
			# Get base header info
			self.info = parse_file_metadata.parse_header(self.header, True)
			# Get extra header length
			if(self.info["extra_len"] > 0):
				self.extra_str = self.handle.read(self.info["extra_len"])
				if(len(self.extra_str) == 0):
					break
			# Read extra header
			try:
				self.extra = pmt.deserialize_str(self.extra_str)
			except Exception as e:
				print ERROR,e
			else:
				print SUCCESS,"Found extra header."
				print "\nExtra Header:"
				self.extra_info = parse_file_metadata.parse_extra_dict(self.extra, self.info, True)
			# move pointer
			self.nread += parse_file_metadata.HEADER_LENGTH + self.info["extra_len"] + self.info['nbytes']
			self.handle.seek(self.nread, 0)
			print "\n\n"

	def create_package(self):
		if (int(math.floor(self.new_timestamp)) - int(math.ceil(self.info['rx_time'])) == 0):
			self.package_name = self.package_prefix + "_{0}.raw".format(self.new_timestamp)
			self.package_fullpath = self.package_path + self.package_name
			self.package = open(self.package_fullpath, "wb")
			for i in range(0,self.package_amount):
				# read out next header bytes
				self.hdr_start = self.handle.tell()
				self.header_str = self.handle.read(parse_file_metadata.HEADER_LENGTH)
				if(len(self.header_str) == 0):
					break
				# Convert from string to PMT (should be a dictionary)
				try:
					print "\033[1;0H"
					self.header = pmt.deserialize_str(self.header_str)
				except Exception as e:
					print ERROR,e
				else:
					self.package.write(self.header_str)
					print SUCCESS,"Write base header."
				# Get base header info
				self.info = parse_file_metadata.parse_header(self.header, True)
				# Get extra header length
				if(self.info["extra_len"] > 0):
					self.extra_str = self.handle.read(self.info["extra_len"])
					if(len(self.extra_str) == 0):
						break
				# Read extra header
				try:
					self.extra = pmt.deserialize_str(self.extra_str)
				except Exception as e:
					print ERROR,e
				else:
					self.package.write(self.extra_str)
					print SUCCESS,"Write base header."
					print "\nExtra Header:"
					extra_info = parse_file_metadata.parse_extra_dict(self.extra, self.info, True)
					self.data_str = self.handle.read(self.info['nbytes'])
					self.package.write(self.data_str)
				
				# move pointer
				self.nread += parse_file_metadata.HEADER_LENGTH + self.info["extra_len"] + self.info['nbytes']
				self.handle.seek(self.nread, 0)
				print "\n\n"
			self.package.close()
			print "\033[21;0H%15s %15s %15s" %("|   Timestamp|","|Upload_Bytes|","|   All_Bytes|")
			self.uploadtask = S3_uploadtask(self.config,self.uploadtaskID,self.new_timestamp,self.package_name,self.package_fullpath)
			self.uploadtask.setDaemon(True)
			self.uploadtask.start()
			self.uploadtaskID += 1
			self.old_timestamp = self.new_timestamp

	def upload_package_2(self):
		while (True):
			self.get_timestamp()
			if (self.old_timestamp != self.new_timestamp) and (int(math.floor(self.new_timestamp)) >= int(math.ceil(self.init_info['rx_time']))):
				self.delta_time = int(math.floor(self.new_timestamp)) - int(math.ceil(self.init_info['rx_time']))
				if (((self.delta_time/4 + self.package_amount) * self.package_length) <= os.path.getsize(self.rawfile_path)):
					self.find_package()
					#create package file
					self.create_package()
			time.sleep(5)

	def upload_package(self):
		while (True):
			self.get_timestamp()
			if (self.old_timestamp <= self.new_timestamp) and (int(math.floor(self.new_timestamp)) >= int(math.ceil(self.init_info['rx_time']))):
				self.delta_time = int(math.floor(self.new_timestamp)) - int(math.ceil(self.init_info['rx_time']))
				if (((self.delta_time + self.package_amount) * self.package_length) <= os.path.getsize(self.rawfile_path)):
					
					self.nread = self.delta_time * self.package_length
					self.handle = open(self.rawfile_path, "rb")
					self.handle.seek(self.nread, 0)
					self.hdr_start = self.handle.tell()
					self.package_str = self.handle.read(self.package_amount * self.package_length)
					self.handle.close()
					#create package file
					self.package_name = self.package_prefix + "_{0}.raw".format(self.new_timestamp)
					self.package_fullpath = self.package_path + self.package_name
					self.package = open(self.package_fullpath, "wb")
					self.package.write(self.package_str)
					self.package.close()

					print "\033[13;0H%15s %15s %15s" %("|   Timestamp|","|Upload_Bytes|","|   All_Bytes|")

					self.uploadtask = S3_uploadtask(self.config,self.uploadtaskID,self.new_timestamp,self.package_name,self.package_fullpath)
					self.uploadtask.setDaemon(True)
					self.uploadtask.start()
					self.uploadtaskID += 1
					self.old_timestamp = self.new_timestamp
			time.sleep(5)


if __name__ == "__main__":
	cli = cutter(cp)
	cli.get_length()
	cli.upload_package_2()
