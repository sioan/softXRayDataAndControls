#!/bin/sh
#ssh -t $1 'sudo /sbin/service ipmi start; sudo ipmitool -I open lan set 1 ipsrc static'
# This script will set the ipmi ip source to static or dhcp
SERVER=$2
IPMIPW=$1
MINARGS=2

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   `basename "$0"` <old password> <server_name>"
   echo -e "Ex: `basename "$0"` ADMIN daq-cxi-mon01"
   echo -e ""
   exit 0 
fi
ipmitool -I lanplus -H ${SERVER}-ipmi -U ADMIN -P ${IPMIPW} user set password 2 ipmia8min


