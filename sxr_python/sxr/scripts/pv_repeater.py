# This script allows one to 1 PV to make changes to another.  This is
# useful in the cases where ACR want temporary control over a local hutch PV
# without modifying the EPICS gateway.
#
# The scripts asks for pairs of PVs -- one PV to listen to and the
# other to control.
#

import pyca
import signal
import sys
from scripts.PVFollower import Follower as PVFollower


# Create list of PVFollower objects
pv_followers = []

# Ctrl-C signal handler ... will be needed when running
def signal_handler(signal,frame) :
    print "\nCtrl-C pressed"
    print "Shutting down pv repeater"

    print "Stopping monitors"
    for pv_follower in pv_followers :
        pv_follower.stop_monitor()

    print "Closing channels"
    for pv_follower in pv_followers :
        pv_follower.clear_channel()



print "********** Starting PV repeater **********"
print "You will be asked for pairs of PVs"
print "  - a PV to read and a PV to control"
print "When you've finished entering all your PV pairs type DONE"
print "(nb:case-sensitve!)"
print "....Then the code will start running"
print ""
print "When finished, press ctrl-c to close the script"




done = False
while (not done) :
    print "PV-pair to read and control"
    print "type DONE when finished \n"
    
    # Get PV to read
    readPV = raw_input("Enter PV to read:     ")

    # remove leading and trailing white spaces
    readPV.strip()
    
    if readPV == "DONE" :
        done = True
        continue


    # Get PV to control
    controlPV = raw_input("Enter PV to control:  ")
    controlPV.strip()

    if controlPV == "DONE" :
        done = True
        continue


    # Create follower
    pv_followers.append(PVFollower(readPV,controlPV, lambda x : x))




try:
    
    print "Starting pv_repeater...."
    print "Open channels..."

    for pv_follower in pv_followers :
        pv_follower.create_channel()


    print "Start monitors..."
    print "Press ctrl-c to stop"
    for pv_follower in pv_followers :
        pv_follower.start_monitor()


    # Now continue until ctrl-c pressed
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

except pyca.pyexc, e:
    print "ERROR: PYCA Error:",e
except pyca.caexc, e:
    print "ERROR, Channel Access Error:",e
