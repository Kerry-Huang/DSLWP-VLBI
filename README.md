DSLWP_VLBI
==========

Install
----------
(1) pip install boto3
(2) edit"package_prefix" "s3_url" "access_key_id" "secret_access_key" "s3_bucket"
	
	./config.ini 
	./Client/Frame/B/config.ini 
	./Client/Packet/B/config.ini

   Format <Station name>_<Package name(NOT EDIT IT!!!)>
    e.g. "package_prefix = Japan" or "package_prefix = Harbin"
    e.g. "package_prefix = Japan_B" or "package_prefix = Harbin_B"
    e.g. "package_prefix = Japan_B" or "package_prefix = Harbin_B"

Run
----------
(1) cd DSLWP-VLBI
(2) sudo python frontend_dslwp_rx_uhd_gpsdo.py
(2) python index_frame.py or python index_packet.py
