"""
Follower
Have an EPICS PV react to changes to another EPCIS PV

Usage:
     Follower.py  <inputpv> <outputpv>
     Follower.py  -h | --help

Options:
     <inputpv>      PV to monitor
     <outputpv>     PV that will react to inputpv changes

     -h | --help    Print this file

"""

from docopt import docopt
arguments = docopt(__doc__)
print arguments

inputpv = arguments['<inputpv>']
outputpv = arguments['<outputpv>']

from Pv import Pv
import pyca
import datetime
import time
from common.motor import Motor as psmotor

input_motor = None
output_motor = None

def motor_moved(exception=None):
    """
    Called whenever CA notices changed in subscribed value
    """
    try:
        print "Motor_moved"
        update_move(input_motor,output_motor)
    except Exception, e:
        print e


def update_move(input_motor, output_motor) :
    """
    Update output's position usin input's position
    """
    print "input",input_motor.get(),"output",output_motor.get()
    newposition = inputmotor.get() * (-0.5 * inputmotor.get())    
    print "output new position", newposition
    output_motor.put(newposition)


evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM


# connect to inputpv
print "Connecting to",inputpv
try: 
    input_motor = Pv(inputpv+".RBV")
    input_motor.monitor_cb = motor_moved
    input_motor.connect(1.0)
    input_motor.monitor(evtmask)

    output_motor = Pv(outputpv+".VAL")
    
    print "waiting 10sec for monitoring to connect"
    time.sleep(10)
    print "Starting monitoring"

    for i in range(100) :
        print i,datetime.datetime.now()
        time.sleep(10)
    
    input.unsubscribe_channel()
    print "Finished monitoring"
        
except pyca.pyexc, e:
    print "pyca exception:", e
except pyca.caexc, e:
    print "channel access exception:",e
except AttributeError, e:
    print "Attribute Error", e



    






