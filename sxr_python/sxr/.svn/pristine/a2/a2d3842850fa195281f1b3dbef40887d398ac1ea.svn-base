import sys
import os
import time
import numpy as np

########################################
# TO DO
# - define 2D scan
#   -y,z start
#   - delta-y, deltz-z
#   - number of points in y, z
# - function to transform from sample to manipulator co-ordinates
# - comments that defines the sample and manipulator reference frames
########################################

########################################
# Definition of co-ordinate systems
#   LCLS Frame
#      x-axis: towards control room 
#      y-axis: vetical up
#      z-axis: x-ray beam direction
#
#   Sample Frame
#      x'-axis : perpendicular to sample plane
#      y'-axis : parallel to y-axis
#      z'-axis : perpendicular to x' and y'
#                parallel to z-axis at zero-degrees angle
#
#      Thus regular grid of imprints has co-ordinates (0,y'_i,z'_i)
########################################


########################################
#  Sample angle in degrees
#  Defined with respect to z-axis (x-ray direction)
#   - increasing angle defined as moving from z-axis toward positive
#     x-axis  
#   - zero defines sample parallel to z-axis

sampleAngle = 0.0
########################################

########################################
# Mark spot settings
# -- Start fiducial defined in sample-frame (y',z')
y_mark_start = 5.0
z_mark_start = 5.0

# -- End fiducial defined in sample-frame (y',z')
y_mark_end = 3.0
z_mark_end = 3.0

# -- Number of FEL pulses and attenuator setting for fiducials 
mark_attenuator = 0.5
mark_burst = 100
########################################



########################################
# 2D Scan settings : Defined in sample-frame
# Set y starting position, distance between imprints, and number of imprints 
# -- Units are in mm

# Start position (mm)
yStart = 4.7
zStart = 4.7

# Distance between imprints in y,z (mm)
deltaY = 0.1
deltaZ = 0.1 

# Number of imprints in y,z
n_imprints_y = 10
n_imprints_z = 10

# -- Number of FEL shots per Burst request
burstValues = (1,2,3,4,5,6,7,8,9,10)

# --- Set Attenuator values here: Units are Torr
#attenuatorValues = (3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.25, 6.5, 6.75, 7.0, \
#                    7.25, 7.5, 7.75, 8.0, 8.25, 8.5, 8.75, 
#                    9.25, 9.5, 9.75, 10.0, 10.25, 10.5, 10.75,11.0 )


attenuatorValues = (1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 4.0)
########################################




########################################
# START OF SCRIPT    ###################
########################################

# Convert from degrees to radians
sampleAngleRad = np.deg2rad(sampleAngle)


# Create rotation matrix
#rotMatrix = 




#### Mark before scan starts
print "Set beginning mark spot"

# Set Attenuator
att_EPICS=  "caput GATT:FEE1:310:P_DES " + str(y_mark_attenuator)
print "wait for attenuator to settle"
os.system(att_EPICS)
time.sleep(120)

# Set y motor
y_EPICS = "caput SXR:EXP:MMS:02 "+str(y_mark_start)
os.system(y_EPICS)

# Request burst
print "Request burst with", y_mark_burst, "FEL shots"
nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(y_mark_burst)
os.system(nFEL_shots_EPICS)
burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1" 
os.system(burst_EPICS)

print y_EPICS," ",att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
time.sleep(1.5)        




#### Start scan 
print "Starting scan"
yPos = yStart

for yStep in range(n_imprints):
 
    # Set Attenuator
    att_EPICS=  "caput GATT:FEE1:310:P_DES " + str(attenuatorValues[yStep])
    print "wait for attenuator to settle"
    os.system(att_EPICS)
    if yStep == 0:
        time.sleep(60)
    else:
        time.sleep(25)

    # Set y motor
    y_EPICS = "caput SXR:EXP:MMS:02 "+str(yPos)
    os.system(y_EPICS)
    
    # Request burst
    print "Request burst with",burstValues[yStep], "FEL shots"
    nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(burstValues[yStep])
    os.system(nFEL_shots_EPICS)
    burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"  
    os.system(burst_EPICS)
    
    print y_EPICS," ",att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
    time.sleep(1.5)        
    
    yPos = yPos + deltaY


print "Scan finished"


#### Mark after scan ends
print "Set end mark spot"

# Set Attenuator
att_EPICS=  "caput GATT:FEE1:310:P_DES " + str(y_mark_attenuator)
print "wait for attenuator to settle"
os.system(att_EPICS)
time.sleep(120)

# Set y motor
y_EPICS = "caput SXR:EXP:MMS:02 "+str(y_mark_end)
os.system(y_EPICS)

# Request burst
print "Request burst with", y_mark_burst, "FEL shots"
nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(y_mark_burst)
os.system(nFEL_shots_EPICS)
burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"
os.system(burst_EPICS)

print y_EPICS," ",att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
time.sleep(1.5)        


print "DONE!"
