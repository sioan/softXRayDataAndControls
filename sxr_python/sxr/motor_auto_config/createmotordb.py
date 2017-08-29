import logging
import subprocess
import os
import datetime

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
            logger.warning("No serial number for %s"%sn_piece[0][:-4])
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



if __name__ == "__main__" :
    logging.basicConfig(level=logging.DEBUG)
    grepout = createmotordb()    
    print grepout
