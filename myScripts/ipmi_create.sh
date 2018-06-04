#!/bin/sh
# This script will set the ipmi in netconfig with standard settings in pcdsn subnet
EP_SUBNET=$1
EP_SERVER=$2
EP_MACIPMI=$3
MYNAME=`basename "$0"`
MINARGS=3

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   "${MYNAME}" <subnet>.pcdsn <server_name> <mac-address>"
   echo -e ""
   exit 0 
fi



netconfig add ${EP_SERVER}-ipmi --mac ${EP_MACIPMI} --subnet ${EP_SUBNET}.pcdsn  --pc IPMI --location "Same as "${EP_SERVER} --manager ${USER} --info "IPMI Interface for "${EP_SERVER} --batch

