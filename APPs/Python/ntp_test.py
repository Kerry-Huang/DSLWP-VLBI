import time
import ntplib
while (1):
	client = ntplib.NTPClient()
	response = client.request('edu.ntp.org.cn')
	print response.tx_time