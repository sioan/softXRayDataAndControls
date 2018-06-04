#!/bin/sh
# This script will set the ipmi SOL console
SERVER=$1
MINARGS=1

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   `basename "$0"` <server_name>"
   echo -e ""
   exit 0 
fi
#echo "To exit console use ~."
# Deactivate if it is activated:
ipmitool -I lanplus -U ADMIN -P ipmia8min -H ${SERVER}-ipmi sol deactivate &> /dev/null
# Call console
xterm -hold -bg black -fg white -T ${SERVER} -e ipmitool -I lanplus -U ADMIN -P ipmia8min -H ${SERVER}-ipmi sol activate &
