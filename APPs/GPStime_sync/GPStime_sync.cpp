#include <uhd/utils/safe_main.hpp>
#include <uhd/usrp/multi_usrp.hpp>
#include <boost/format.hpp>
#include <boost/thread.hpp>
#include <iostream>

#define INFO   "[\033[33mINFO\033[0m]"
#define ERROR   "[\033[31mERROR\033[0m]"
#define SUCCESS   "[\033[32mSUEECSS\033[0m]"
#define WARNING   "[\033[33mWARNING\033[0m]"

int UHD_SAFE_MAIN(int argc, char *argv[])
{
    //Initialize USRP device
    std::cout << INFO << "USRP Initialization" << std::endl;
    std::string args;
    uhd::usrp::multi_usrp::sptr usrp = uhd::usrp::multi_usrp::make(args);
    std::cout << INFO << boost::format("Using Device:\n%s") % usrp->get_pp_string() << std::endl;
    std::cout << INFO << "Synchronizing mboard: " << usrp->get_mboard_name() << std::endl;

    //Set references to GPSDO
    usrp->set_clock_source("gpsdo");
    usrp->set_time_source("gpsdo");
    std::cout << INFO << "the default 10 MHz Reference and 1 PPS signals are now from the GPSDO." << std::endl;

    //Check for 10 MHz lock
    std::vector<std::string> sensor_names = usrp->get_mboard_sensor_names();
    if(std::find(sensor_names.begin(), sensor_names.end(), "ref_locked") != sensor_names.end())
    {
        std::cout << INFO << "Waiting for reference lock..." << std::flush;
        bool ref_locked = false;
        for (int i = 0; i < 30 and not ref_locked; i++)
        {
            ref_locked = usrp->get_mboard_sensor("ref_locked").to_bool();
            if (not ref_locked)
            {
                std::cout << "." << std::flush;
                boost::this_thread::sleep(boost::posix_time::seconds(1));
            }
        }
        if(ref_locked)
        {
            std::cout << "\n" << SUCCESS << "Reference Locked." << std::endl;
        } 
        else
        {
            std::cout << "\n" << ERROR << "Failed to lock to GPSDO 10 MHz Reference. Exiting." << std::endl;
            exit(EXIT_FAILURE);
        }
    }
    else
    {
        std::cout << ERROR << "ref_locked sensor not present on this board.\n"<< std::endl;
    }

    //Check for GPS lock
    std::cout << INFO << "Waiting for GPS lock..." << std::flush;
    bool gps_locked = false;
    for (int i = 0; i < 30 and not gps_locked; i++)
    {
        gps_locked = usrp->get_mboard_sensor("gps_locked").to_bool();
        if (not gps_locked)
        {
            std::cout << "." << std::flush;
            boost::this_thread::sleep(boost::posix_time::seconds(1));
        }
    }
    if(gps_locked)
    {
        std::cout << SUCCESS <<"GPS Locked"<< std::endl;
    }
    else
    {
        std::cout << WARNING << "GPS not locked - time will not be accurate until locked" << std::endl;
    }

    //Set to GPS time
    uhd::time_spec_t gps_time = uhd::time_spec_t(time_t(usrp->get_mboard_sensor("gps_time").to_int()));
    usrp->set_time_next_pps(gps_time+1.0);

    boost::this_thread::sleep(boost::posix_time::seconds(2));

    //NMEA information
    uhd::sensor_value_t gga_string = usrp->get_mboard_sensor("gps_gpgga");
    uhd::sensor_value_t rmc_string = usrp->get_mboard_sensor("gps_gprmc");
    std::cout << INFO << boost::format("Printing available NMEA strings:")<< std::endl;
    std::cout << boost::format("      %s\n      %s\n") % gga_string.to_pp_string() % rmc_string.to_pp_string();
    
    //Times information
    gps_time = uhd::time_spec_t(time_t(usrp->get_mboard_sensor("gps_time").to_int()));
    uhd::time_spec_t time_last_pps = usrp->get_time_last_pps();
    std::cout << INFO << "USRP time: " << (boost::format("%0.9f") % time_last_pps.get_real_secs()) << std::endl;
    std::cout << INFO << "GPSDO time: " << (boost::format("%0.9f") % gps_time.get_real_secs()) << std::endl;
    std::cout << INFO << "PC Clock time: "<< boost::format("%0.9f") % time(NULL) << std::endl;
    
    //Check Times
    if (gps_time.get_real_secs() == time_last_pps.get_real_secs())
        std::cout << SUCCESS << "USRP time synchronized to GPS time." << std::endl;
    else
        std::cout << ERROR << "Failed to synchronize USRP time to GPS time." << std::endl;
}
