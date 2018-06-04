#!/bin/sh
# This script will list the ipmi firmware veriosn or complete bmc info
BMC_SRV=$2
BMC_CMD=$1
MINARGS=2

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   "$0" <server_name> <version|info>"
   echo -e "Ex: "$0" daq-xpp-dss01 version (shows only version)" 
   echo -e "    "$0" daq-xpp-dss01 info    (shows complete info)" 
   echo -e ""
   exit 0 
fi
if [ "${BMC_CMD}" == "version" ] ; then
   ipmitool -I lanplus -H ${BMC_SRV}-ipmi  -U ADMIN -P ipmia8min mc info | grep "Firmware Revision"
else
   ipmitool -I lanplus -H ${BMC_SRV}-ipmi  -U ADMIN -P ipmia8min mc info
fi
