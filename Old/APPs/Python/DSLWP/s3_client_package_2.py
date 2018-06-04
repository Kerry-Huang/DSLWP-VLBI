import os
import pmt
import ast
import time
import math
import boto3
import urllib2
import threading
import ConfigParser
from gnuradio.blocks import parse_file_metadata

import tarfile
import bz2
import io

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
		self.old_timestamp = 0
		self.new_timestamp = 0
		self.uploadtaskID = 0

		#Get the config from config.ini
		self.config = config
		##cutter
		self.rawfile_fullpath = self.config.get('cutter','rawfile_path')
		self.package_path = self.config.get('cutter','package_path')
		self.timeapi_url = self.config.get('cutter','timeapi_url')
		self.package_prefix = self.config.get('cutter','package_prefix')
		self.package_amount = self.config.getint('cutter','package_amount')	
		self.rawfile_path = self.config.get('cutter','rawfile_path')
		self.rawfile_name = ast.literal_eval(self.config.get('cutter','rawfile_name'))
		
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
		#init var
		self.nread = 0
		self.handle = open(self.rawfile_fullpath, "rb")
		self.handle.seek(0, 0)
		self.hdr_start = self.handle.tell()
		
		#read the base header
		self.header_str = self.handle.read(parse_file_metadata.HEADER_LENGTH)
		print "\033[1;0H"
		self.header = pmt.deserialize_str(self.header_str)
		print SUCCESS,"Found init header."
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


	def read_package(self):
		if (int(math.floor(self.new_timestamp)) - int(math.ceil(self.info['rx_time'])) == 0):
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
					self.package_str[self.raw_num] += self.header_str
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
					self.package_str[self.raw_num] += self.extra_str
					print SUCCESS,"Write extra header."
					print "\nExtra Header:"
					extra_info = parse_file_metadata.parse_extra_dict(self.extra, self.info, True)
					self.data_str = self.handle.read(self.info['nbytes'])
					self.package_str[self.raw_num] += self.data_str
				
				# move pointer
				self.nread += parse_file_metadata.HEADER_LENGTH + self.info["extra_len"] + self.info['nbytes']
				self.handle.seek(self.nread, 0)
				print "\n\n"
		
	def create_package(self):	
		#init var
		self.package_name[self.raw_num] = self.package_prefix + "_{0}_".format(self.new_timestamp)+self.rawfile_name[self.raw_num]+"_package"
		if self.raw_num == len(self.rawfile_name)-1:
			self.bz2_name = self.package_prefix + "_{0}.tar.bz2".format(self.new_timestamp)
			self.bz2_fullpath = self.package_path + self.bz2_name
			self.archive = tarfile.open(self.bz2_fullpath,'w:bz2')
			self.archive.debug = 1
			for self.raw_num in range(len(self.rawfile_name)):
				self.bz2_data = io.BytesIO(self.package_str[self.raw_num])
				self.bz2_info = tarfile.TarInfo(name=self.package_name[self.raw_num])
				self.bz2_info.size = len(self.package_str[self.raw_num])
				self.archive.addfile(self.bz2_info,self.bz2_data)
			self.archive.close()
			self.handle.close()
			

	def upload_package(self):
		while (True):
			self.bz2_fullpath = ""
			self.package_str = []
			self.package_name = []
			for self.raw_num in range(len(self.rawfile_name)):
				self.package_str.append("")
				self.package_name.append("")
			self.get_timestamp()
			for self.raw_num in range(len(self.rawfile_name)):
				self.rawfile_fullpath = self.rawfile_path + self.rawfile_name[self.raw_num]
				self.get_length()
				if (self.old_timestamp != self.new_timestamp) and (int(math.floor(self.new_timestamp)) >= int(math.ceil(self.init_info['rx_time']))):
					self.delta_time = int(math.floor(self.new_timestamp)) - int(math.ceil(self.init_info['rx_time']))
					if (((self.delta_time + self.package_amount) * self.package_length) <= os.path.getsize(self.rawfile_fullpath)):
						self.find_package()
						#create package file
						self.read_package()
						self.create_package()
			if os.path.exists(self.bz2_fullpath):
				print "\033[21;0H%15s %15s %15s" %("|   Timestamp|","|Upload_Bytes|","|   All_Bytes|")

				self.uploadtask = S3_uploadtask(self.config,self.uploadtaskID,self.new_timestamp,self.bz2_name,self.bz2_fullpath)
				self.uploadtask.setDaemon(True)
				self.uploadtask.start()
				self.uploadtaskID += 1
				self.old_timestamp = self.new_timestamp
			time.sleep(5)

if __name__ == "__main__":
	cli = cutter(cp)
	cli.upload_package()
