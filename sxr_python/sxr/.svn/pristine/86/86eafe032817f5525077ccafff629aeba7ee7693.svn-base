"""
Scan_3D

Script to carry out a scan using 2 motors

Usage:  
   Scan_3D.py  <motorpvname>  <from>  <to> 
               <motorpvname2> <from2> <to2> 
               <motorpvname3> <from3> <to3> 
               <points> <events_per_point> <record>  

Options:
    <motorpvname>        PV of motor_1
    <from>               start position for motor_1
    <to>                 end position for motor_1
    <motorpvname2>       PV of motor_2
    <from2>              start position for motor_2
    <to2>                end position for motor_2
    <motorpvname3>       PV of motor_3
    <from3>              start position for motor_3
    <to3>                end position for motor_3
    <points>             Number of points between 'from' and 'to'
    <events_per_point>   Number of DAQ events to record per step 
    <record>             Record the DAQ data - true/false     

    -h , --help          Print this file


Each motor moves between 'from(2)(3) and to(2)(3) in 'points' steps and records
events_per_point DAQ events per step

Example:
Scan motors SXR:EXP:MMS:01, SXR:EXP:MMS:02, SXR:EXP:MMS:03, between -10 and 10, 
50 and 100.0, and 20 and 40, respectively, using 15 points and record
20 DAQ events per point.  All DAQ data to be saved.

  Scan_3D SXR:EXP:MMS:01 -10.0  10.0  \
          SXR:EXP:MMS:02  50.0 100.0  \
          SXR:EXP:MMS:03  20.0 40.0   \
          15 20 True
"""

# Read in command line arguments
from docopt import docopt
arguments = docopt(__doc__,options_first=True)
#print arguments

motorpvname1 = arguments['<motorpvname>']
from1 = float(arguments['<from>'])
to1 = float(arguments['<to>'])
              
motorpvname2 = arguments['<motorpvname2>']
from2 = float(arguments['<from2>'])
to2 = float(arguments['<to2>'])

motorpvname3 = arguments['<motorpvname3>']
from3 = float(arguments['<from3>'])
to3 = float(arguments['<to3>'])


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
motor2 = psmotor(motorpvname2)
motor3 = psmotor(motorpvname3)

daq.a3scan(motor1,from1,to1,
           motor2,from2,to2,
           motor3,from3,to3,
           points, events_per_point)

