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

    //Times information
    uhd::time_spec_t gps_time = uhd::time_spec_t(time_t(usrp->get_mboard_sensor("gps_time").to_int()));
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
