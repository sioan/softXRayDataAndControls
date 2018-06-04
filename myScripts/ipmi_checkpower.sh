#!/bin/bash
# This script will check the power status on given hutch
MINARGS=2
HUTCH=$1
SRVT=$2

START=0
#declare -a SRVS
red=$(tput setaf 1)
green=$(tput setaf 2)
brown=$(tput setaf 3)
blue=$(tput setaf 4)
magenta=$(tput setaf 5)
cyan=$(tput setaf 6)
gray=$(tput setaf 7)
gray=$(tput setaf 8)
ltgreen=$(tput setaf 9)
normal=$(tput sgr0)
off="off"

if [ $# -ne $MINARGS ] ; then
   echo -e ""
   echo -e "Usage:   `basename "$0"` <hutch_name> <server_type>"
   echo -e "Example: `basename "$0"` amo daq"
   echo -e ""
   exit 0 
fi

SRVS=$(netconfig search "${SRVT}-$HUTCH-*-ipmi" --brief | grep -Ev 'ana|fez|acq' | sort)
NSRVS=($SRVS)

echo " Checking power status in ${#NSRVS[@]} servers:"

printf " %-25s | %s\n" "Server" "Power Status"

for (( c=$START; c<${#NSRVS[@]} ; c++)) do
   server=${NSRVS[c]%\-ipmi}
#   STATUS=$(ipmi_setpower.sh status ${server} 2>&1)
   STATUS=$(ipmi_setpower.sh status ${server})   
   printf " %-25s | " "$server"
   if [ "${STATUS/$off}" != "$STATUS" ] ; then
      printf "%s\n"  "${red}$STATUS${normal}"
   else
      printf "%s\n"  "$STATUS"
   fi
done
exit 0

