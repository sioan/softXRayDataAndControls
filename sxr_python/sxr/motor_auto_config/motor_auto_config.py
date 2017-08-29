import logging
import subprocess
import os
import datetime

from  sxr_common.epics_ims_motor import epics_ims_motor

logger = logging.getLogger(__name__)

def createmotordb():
    """
    Go through all config files in $DEVICE_CONFIG_DIR and map motor
    serial number of latest config file.

    Returns a dictionary where
    - key: motor serial number
    - value: latest config file
    """
    logger.info("Creating motor configuration DB")    
    
    logger.debug("Grepping motor serial number from motor config files")    
    command_string = "grep -H '\.SN' $DEVICE_CONFIG_DIR/*.cfg  | sort -n -k 2"
    logging.debug(command_string)
    
    grep_out = subprocess.check_output(command_string,shell=True)
    sn_list = grep_out.strip().split("\n")
        

    # loop through sn_list and build up dictionary of SN to latest
    # config
    logger.debug("Matching serial numbers of latest configuration")
    motor_db = {}  # Empty motor-db dictionary

    for sn in sn_list:

        # split line apart
        sn_piece = sn.split()

        # If size < 2 -- no SN recorded and should be skipped
        if len(sn_piece) < 2:
            logger.debug("No serial number for %s"%sn_piece[0][:-4])
            continue

        # Get config file and serial number
        cfg = sn_piece[0][:-4]  # last 4 characters from grep output
                                # are always ':.SN 
        sn = sn_piece[1]

        # Add unique entries to motor-db dictionary
        if sn in motor_db.keys() :
            # Only add latest config
            logger.debug("Found another config file for SN:%s"%sn)

            db_time = os.stat(motor_db[sn]).st_mtime
            new_time = os.stat(cfg).st_mtime
            
            logger.debug("%s ==> %s"%(motor_db[sn],
                                      datetime.datetime.fromtimestamp(db_time) )
                         )
            logger.debug("%s ==> %s"%(cfg,
                                      datetime.datetime.fromtimestamp(new_time))
                         )

            if new_time > db_time :
                logger.debug("Picking new config %s"%cfg)
                motor_db[sn] = cfg
            else:
                logger.debug("Sticking with current config %s"%motor_db[sn])
        else :
            # New entry
            logger.debug("New entry=>  SN:%s CFG:%s"%(sn,cfg))
            motor_db[sn] = cfg

    logger.info("Number of saved motor configs:%d"%len(sn_list))
    logger.info("Number of unique motor configs:%d"%len(motor_db))
    return motor_db



def setupmotor(motordb, motor_pv) :
    """
    Function to setup motor
    
    After parameter manager goes live:
        - parameter manager API should offer the following:
            - search for SN in Db
            - search for dumb or smart using SN as key
            - download all data to motor, using SN as key

    After parameter manager goes live
        - remove createdb function
            - replace calls to check SN, motor-type with parameter-manager API
            - epics_ims_motor.config function may be removed if
              parameter-manager API can do this  
    """

    logger.info("Setup motor %s"%motor_pv)

    # Create motor-pv object
    motor = epics_ims_motor(motor_pv)

    # Intialize motor
    init_success = motor.init()
    if not init_success :
        logger.debug("Failed to initialize %s",motor_pv)
        return False

    
    # Now get motor serial number & part number
    motor_sn = motor.sn()
    motor_pn = motor.pn()
    logger.debug("%s SN:%s  PN:%s"%(motor_pv,motor_sn,motor_pn))
        
    # Use motor's serial number to find latest configuration
    # Use motor model (part) number to determine if motor is smart or
    # dumb
    #   - MFI... ==> DUMB motor
    #   - MDI... ==> SMART motor
    if motor_pn.startswith("MFI") :
        logger.warning("%s - Dumb motor has to be configured manually"%motor_pv)
        return False

    # ..got here...must be a smart motor
    config_success = False
    if motor_sn in motordb.keys() :
        logger.debug("Found configuration for motor %s"%motor_pv)
        config_success = motor.config(motordb[motor_sn])                
    else:
        logger.warning("No config file for %s"%motor_pv)

    return config_success
        


if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO)

    """
    To run this script, you need to 
    - Give motor PV prefix
    - range of motors to configure
    """
    
    # Parse command line arguments
    import argparse
    parser = \
      argparse.ArgumentParser(description="Auto config patch panel motors")
    parser.add_argument('-p','--PV', dest="pv",help="Patch Panel Motor PV")
    parser.add_argument('-r','--range',dest="range",nargs="+",type=int,
                        help="Range of motor patch panel ports")
    option = parser.parse_args()
    
    # Create motor DB
    motordb = createmotordb()

    unconfigured = []
    
    # Set up motors
    for port in range(option.range[0],option.range[1]+1) :

        motor_pv = "%s:%02d"%(option.pv,port) 
        config_success = setupmotor(motordb, motor_pv)
                
        if (not config_success ) :
            unconfigured.append(motor_pv)


    print "All motors done"
    if unconfigured :
        print "These motors failed to configure:"
        for motor in unconfigured :
            print "\t ",motor
    


