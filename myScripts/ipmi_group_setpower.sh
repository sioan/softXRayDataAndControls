#!/bin/sh
#ssh -t $1 'sudo /sbin/service ipmi start; sudo ipmitool -I open lan set 1 ipsrc static'
# This script will set the ipmi ip source to static or dhcp
PWCTRL=$1
SERVER=$2
STARTI=$3
STOP_I=$4
MINARGS=4

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   `basename "$0"` <status|on|off|reset|cycle> <hutch_prefix> <first_index> <last_index>"
   echo -e "Ex.:     `basename "$0"` status daq-cxi-mon 4 10"
   echo -e ""
   exit 0
fi

for i in $(seq -s " " -f %02g ${STARTI} ${STOP_I}); do
   echo ${SERVER}$i
   ipmitool -I lanplus -H ${SERVER}$i-ipmi -U ADMIN -P ipmia8min power ${PWCTRL}
done
exit 0
