"""
Scan_3DGrid

Script to carry out a scan a grid of point using 2 motors

Usage:  
   Scan_3D.py  <motorpvname>   <from>  <to>  <npoints>
               <motorpvname2> <from2> <to2> <npoints2>
               <motorpvname3> <from3> <to3> <npoints3>
               <events_per_point> <record>  

Options:
    <motorpvname>        PV of motor_1
    <from>               start position for motor_1
    <to>                 end position for motor_1
    <npoints>            Number of points for motor1
    <motorpvname2>       PV of motor_2
    <from2>              start position for motor_2
    <to2>                end position for motor_2
    <npoints2>           Number of points for motor2
    <motorpvname3>       PV of motor_3
    <from3>              start position for motor_3
    <to3>                end position for motor_3
    <npoints3>           Number of points for motor3
    <events_per_point>   Number of DAQ events to record per step 
    <record>             Record the DAQ data - true/false     

    -h , --help          Print this file


Three motors are used to scan over a 3D grid of points, defined by
- motor1 uses 'npoints' to scan range betwween 'from' and 'to' 
- motor2 uses 'npoints' to scan range betwween 'from2' and 'to2' 
- motor3 uses 'npoints' to scan range betwween 'from3' and 'to3' 

At each point 'events_per_point DAQ' events are recorded

Example:
Use motors SXR:EXP:MMS:01 and SXR:EXP:MMS:02 to scan a 4x6 grid
covering the ranges -10 and 10, and -5 and 20, respectively. At each
point, record 20 DAQ events.

  Scan_3DGrid SXR:EXP:MMS:01 -10.0 10.0 4 SXR:EXP:MMS:02 -5 20 6 20 True
"""

# Read in command line arguments
from docopt import docopt
arguments = docopt(__doc__,options_first=True)
#print arguments

motorpvname1 = arguments['<motorpvname>']
from1 = float(arguments['<from>'])
to1 = float(arguments['<to>'])
points1 = int(arguments['<npoints1>'])
              
motorpvname2 = arguments['<motorpvname2>']
from2 = float(arguments['<from2>'])
to2 = float(arguments['<to2>'])
points2 = int(arguments['<npoints2>'])

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

daq.mesh3D(motor1,from1,to1,npoints1,
           motor2,from2,to2,npoints2,
           motor3,from3,to3,npoints3,
           events_per_point)


