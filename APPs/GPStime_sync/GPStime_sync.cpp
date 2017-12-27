#include <uhd/utils/safe_main.hpp>
#include <uhd/usrp/multi_usrp.hpp>
#include <boost/format.hpp>
#include <boost/thread.hpp>
#include <iostream>

#define RESET   "\033[0m"
#define RED     "\033[31m"      /* Red */
#define GREEN   "\033[32m"      /* Green */
#define YELLOW  "\033[33m"      /* Yellow */

int UHD_SAFE_MAIN(int argc, char *argv[])
{
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "USRP Initialization" << std::endl;
    std::string args;
    uhd::usrp::multi_usrp::sptr usrp = uhd::usrp::multi_usrp::make(args);
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << boost::format("Using Device:\n%s") % usrp->get_pp_string() << std::endl;
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "Synchronizing mboard: " << usrp->get_mboard_name() << std::endl;

    //Set references to GPSDO
    usrp->set_clock_source("gpsdo");
    usrp->set_time_source("gpsdo");
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "the default 10 MHz Reference and 1 PPS signals are now from the GPSDO." << std::endl;

    //Check for 10 MHz lock
    std::vector<std::string> sensor_names = usrp->get_mboard_sensor_names();
    if(std::find(sensor_names.begin(), sensor_names.end(), "ref_locked") != sensor_names.end())
    {
        std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "Waiting for reference lock..." << std::flush;
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
            std::cout << "\n[" << GREEN << "SUCCESS" << RESET << "]" << "Reference Locked." << std::endl;
        } 
        else
        {
            std::cout << "\n[" << RED << "ERROR" << RESET << "]" << "Failed to lock to GPSDO 10 MHz Reference. Exiting." << std::endl;
            exit(EXIT_FAILURE);
        }
    }
    else
    {
        std::cout << "[" << RED << "ERROR" << RESET << "]" << "ref_locked sensor not present on this board.\n"<< std::endl;
    }

    //Wait for GPS lock
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "Waiting for GPS lock..." << std::flush;
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
        std::cout << "\n[" << GREEN << "SUCCESS" << RESET << "]" <<"GPS Locked"<< std::endl;
    }
    else
    {
        std::cout << "\n[" << YELLOW << "WARNING" << RESET << "]" << "GPS not locked - time will not be accurate until locked" << std::endl;
    }

    //Set to GPS time
    uhd::time_spec_t gps_time = uhd::time_spec_t(time_t(usrp->get_mboard_sensor("gps_time").to_int()));
    usrp->set_time_next_pps(gps_time+1.0);

    boost::this_thread::sleep(boost::posix_time::seconds(2));

    uhd::sensor_value_t gga_string = usrp->get_mboard_sensor("gps_gpgga");
    uhd::sensor_value_t rmc_string = usrp->get_mboard_sensor("gps_gprmc");
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << boost::format("Printing available NMEA strings:")<< std::endl;
    std::cout << boost::format("      %s\n      %s\n") % gga_string.to_pp_string() % rmc_string.to_pp_string();
    //Check times
    gps_time = uhd::time_spec_t(time_t(usrp->get_mboard_sensor("gps_time").to_int()));
     uhd::time_spec_t time_last_pps = usrp->get_time_last_pps();
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "USRP time: " << (boost::format("%0.9f") % time_last_pps.get_real_secs()) << std::endl;
    std::cout << "[" << YELLOW << "INFO" << RESET << "]" << "GPSDO time: " << (boost::format("%0.9f") % gps_time.get_real_secs()) << std::endl;
    if (gps_time.get_real_secs() == time_last_pps.get_real_secs())
        std::cout << "[" << GREEN << "SUCCESS" << RESET << "]" << "USRP time synchronized to GPS time." << std::endl;
    else
        std::cout << "[" << RED << "ERROR" << RESET << "]" << "Failed to synchronize USRP time to GPS time." << std::endl;
}
