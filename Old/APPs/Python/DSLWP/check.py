import os
import boto3
import ntplib
import urllib2
import ConfigParser

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

class client_check:
	def __init__(self,config):
		#Get the config from config.ini
		##usrp
		self.ntp_url = config.get('usrp','ntp_url')
		##cutter
		self.timeapi_url = config.get('cutter','timeapi_url')
		self.package_prefix = config.get('cutter','package_prefix')
		##s3
		self.s3_url = config.get('s3','s3_url')
		self.access_key_id = config.get('s3','access_key_id')
		self.secret_access_key = config.get('s3','secret_access_key')

	def check_usrp(self):
		#Check the USRP devices
		print INFO,"Check USRP Devices"
		#Use the system command
		os.system("uhd_find_devices")
		print

	def check_ntp(self):
		#Check NTP Server
		try:
			print INFO,"Check NTP Server"
			#Connect to the NTP Server
			self.ntp_client = ntplib.NTPClient()
			self.ntp_response = self.ntp_client.request(self.ntp_url)
			#Print the URL
			print SUCCESS,"NTP Server:",self.ntp_url
			#Print the Timestamp
			print SUCCESS,"Timestamp:",self.ntp_response.tx_time
			print 
		except Exception as e:
			print ERROR,e
			exit()

	def check_timestamp(self):
		#Check Timestamp Server
		try:
			print INFO,"Check Timestamp Server"
			#Connect to the Timestamp Server
			self.timeapi = urllib2.urlopen(self.timeapi_url)
			#Print the URL
			print SUCCESS,"Timestamp Server:",self.timeapi_url
			#Print the Timestamp
			print SUCCESS,"Timestamp:",int(self.timeapi.read())
			print 
		except Exception as e:
			print ERROR,e
			exit()

	def check_s3(self):
		#Check S3 Server
		try:
			print INFO,"Check S3 Server"
			#Connect to the S3 Server
			self.s3 = boto3.resource(
				's3',
				endpoint_url = self.s3_url,
				aws_access_key_id = self.access_key_id,
				aws_secret_access_key = self.secret_access_key,
				config=boto3.session.Config(signature_version='s3v4')
				)
			#Create the test file
			self.testfile_name = self.package_prefix+"test"
			self.testfile = open(self.testfile_name, "wb")
			self.testfile.close()
			#Upload the test file
			self.s3.Bucket('vlbi').upload_file(self.testfile_name,self.testfile_name)
			print SUCCESS,"upload test package successful."
			print
		except Exception as e:
			print ERROR,e
			exit()


if __name__ == "__main__":
	os.system("clear")
	cli_check = client_check(cp)
	cli_check.check_usrp()
	cli_check.check_ntp()
	cli_check.check_timestamp()
	cli_check.check_s3()
	#os.system("gnome-terminal -e 'python s3_client_2.py'") 
