import casi, casiTools
import os
import datetime

#/reg/g/pcds/controls/pycasi/pycasi.py --archive /reg/d/pscaa/SXR/2013/12_05/index --pv SXR:EXP:MMS:01.SREV


def find_archive_index(archive_date) :
        
    print "Searching archive for",archive_date.strftime('%Y-%m-%d')
    base_path =os.path.join("/reg/d/pscaa/SXR/", str(archive_date.year))

    # find year closest index to date
    for day in range(365) :

        # Does archive index for archive_date 
        archive_path = os.path.join(base_path,
                                    "%02d_%02d"%(archive_date.month,archive_date.day))
        if os.path.isdir(archive_path) :
            print "Found index",archive_path
            return archive_path
            break
        else :
            archive_date -= datetime.timedelta(days=1)


    # Got here...no archive found
    print "No archive found"
    return None
    

def parse_template(filename) :

    template_file = open(filename,'r')

    motor_param_pv = []
    
    for line in template_file :        
        if line.startswith(".") or line.startswith(":") :
            motor_param_pv.append(line.strip())

    return motor_param_pv


def get_unique_vals(value,PV=None) :
    previous_value = None 

    while value.valid() :
        if (value.isInfo() is False) and (value.text() != previous_value) :
            
            print PV,casiTools.formatValue(value)
            previous_value = value.text()

        value.next()


def get_all_motor_params(motor_pv_prefix,motor_config_pv_list) :

    channel = casi.channel()
    value = casi.value()
    
    for pv in motor_config_pv_list :
        motor_pv = motor_pv_prefix + pv

        #print motor_pv
        success = archive.findChannelByName(motor_pv,channel)
        if success :
            #print "*********",motor_pv,"*********"            
            channel.getFirstValue(value)
            get_unique_vals(value,motor_pv)
        else :
            print "*********",motor_pv,"is not archived","*********"


    
if __name__ == '__main__':

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Extract Motor PVs from archive")    
    parser.add_argument('-d','--date',dest="date",help='Date in MM/DD/YYYY format')
    parser.add_argument('-p','--pv',dest="pv_prefix",help="PV Base, such as SXR:EXP:MMS")
    parser.add_argument('-r','--range',dest="range",nargs="+",
                        type=int,help="Range of values.Eg: scan motors 01 to 10, --range 1 10")

    option = parser.parse_args()

    # Extract Date
    archive_date = datetime.datetime.strptime(option.date,"%m/%d/%Y")
    

    # Find archive for input date
    archive_index = find_archive_index(archive_date)
    if archive_index is None :
        import sys
        sys.exit()

    
    # Append index to archive_index
    archive_index = os.path.join(archive_index, "index")


    # Parse the motor archive template
    motor_archive_template = os.path.join( os.environ["DEVICE_CONFIG_TEMPLATE_DIR"],
                                           "sxd_ims_config_archive.tmp" )
    motor_config_pv_list = parse_template(motor_archive_template)


    # Create archive object at archive_index
    archive = casi.archive()
    archive.open(archive_index)


    # Loop over PVs of interest
    motor_pv_ppl_prefix = option.pv_prefix

    motor_start = option.range[0]
    motor_end = option.range[1]

    #for port in range(30,31) :
    for port in range(motor_start, motor_end) :
        motor_pv_prefix = "%s:%02d"%(motor_pv_ppl_prefix,port)
        get_all_motor_params(motor_pv_prefix, motor_config_pv_list)
        

