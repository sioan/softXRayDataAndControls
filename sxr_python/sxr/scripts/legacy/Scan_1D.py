"""
Scan_1D

Script to carry out a scan using 1 motor

Usage:  
   Scan_1D.py  <motorpvname>  <from>  <to> 
               <points> <events_per_point> <record>  

Options:
    <motorpvname>        PV of motor_1
    <from>               start position for motor_1
    <to>                 end position for motor_1
    <events_per_point>   Number of DAQ events to record per step 
    <record>             Record the DAQ data - true/false     

    -h , --help          Print this file


The motor moves between 'from' and 'to' in 'points' steps and records
events_per_point DAQ events per step

Example:
Scan motors SXR:EXP:MMS:01 between -10 and 5 in 15 steps and record
20 DAQ events per step.   

  Scan_1D SXR:EXP:MMS:01 -10.0 5.0 15 20 True
"""

# Read in command line arguments
from docopt import docopt
arguments = docopt(__doc__,options_first=True)
#print arguments

motorpvname1 = arguments['<motorpvname>']
from1 = float(arguments['<from>'])
to1 = float(arguments['<to>'])
              
points = int(arguments['<points>'])
events_per_point = int(arguments['<events_per_point>'])

record = False
if ( (arguments['<record>']).lower() == "true" or
     (arguments['<record>']).lower() == "t" ) :
    record=True


# Now import modules
import common.daq_new as Daq
from common.motor import Motor as psmotor



# Set up DAQ
print "Check the DAQ GUI is running and DAQ is configured"
raw_input("(press enter to contine)")

print "Connecting to DAQ - plese be patient"
daq = Daq.Daq(host='sxr-daq')
daq.record=record

# Set up motors
motor1 = psmotor(motorpvname1)

daq.ascan(motor1,from1,to1,
           points, events_per_point)

