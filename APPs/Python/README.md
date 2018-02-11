Lilacsat_VLBI
=======================================================

Record
-------------------------------------------------------
$ python frontend_rx_uhd_VLBI_250k.py
(sample rate 250k)

OR

$ python frontend_rx_uhd_VLBI_1M.py 
(sample rate 1M)

Note:
If it output "[Error] GPS Unlocked."
(1) Close the program,and wait a few minutes.
(2) Check GPS antenna.

Convert format
-------------------------------------------------------
$ python meta_to_data.py 
