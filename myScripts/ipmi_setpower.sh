#!/bin/sh
#ssh -t $1 'sudo /sbin/service ipmi start; sudo ipmitool -I open lan set 1 ipsrc static'
# This script will set the ipmi ip source to static or dhcp
SERVER=$2
PWCTRL=$1
MINARGS=2

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   `basename "$0"` <status|on|off|reset|cycle> <server_name>"
   echo -e ""
   exit 0 
fi
ipmitool -I lanplus -H ${SERVER}-ipmi -U ADMIN -P ipmia8min power ${PWCTRL}


