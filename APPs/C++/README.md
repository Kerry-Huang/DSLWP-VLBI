1.安装依赖
sudo apt-get install libboost-all-dev
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt-get update
sudo apt-get install libuhd-dev libuhd003 uhd-host

2.编译
cd至该目录
g++ GPStime_sync.cpp -luhd -lboost_thread -lboost_system -o GPStime_sync

3.运行
./GPStime_sync
