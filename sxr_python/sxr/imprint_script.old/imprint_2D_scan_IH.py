#!/bin/env python

#import sys
import os
import time
import numpy as np


################################################################################
# Definition of co-ordinate systems
#   LCLS Frame
#      x-axis: towards control room 
#      y-axis: vetical up
#      z-axis: x-ray beam direction
#
#   Sample Frame
#      x'-axis : parallel to x-axis when sample-x angle is zero
#      y'-axis : parallel to y-axis when sample-y angle is zero
#      z'-axis : perpendicular to sample plane, where z=0 is sample surface
#      ===> The axis only true when all sample rotation angles are zero
#
# Thus regular grid of imprints has co-ordinates (x_i', y_i', 0)
################################################################################


################################################################################
#  Sample angle in degrees
#  !!!NEED TO CHECK HOW THESE ARE DEFINED!!!
#  Defined with respect to z-axis (x-ray direction)
#   - increasing angle defined as moving from z-axis toward positive
#     x-axis  
#   - zero defines sample parallel to z-axis
#
sampleAngle_x = 70.0
sampleAngle_y = 0.0
sampleAngle_z = 0.0

manipOrigin_x = -0.5915
manipOrigin_y = -5.8840
manipOrigin_z = 576.3342

################################################################################

################################################################################
######## Number of imprints in (x',y') ########
n_imprints_x = 3
n_imprints_y = 2

######## Position of fiducial marker in sample-frame (x',y') ########
x_mark_start = 0.0
y_mark_start = -1.0

######## Distance between imprints in (x',y') (mm) ########
deltaX = 1.0
deltaY = 1.0

######## Number of FEL pulses and attenuator setting for fiducials ########
mark_attenuator = 0.1 			# attenuator pressure
mark_burst = 100				# number of bursts for marker

######## Set Attenuator values here: Units are Torr ########
att_min = mark_attenuator
att_max = 15.0
################################################################################




################################################################################
# 2D Scan settings : Defined in sample-frame
# Set (x',y') starting position, distance between imprints, and number
# of imprints  
# Units are in mm
#
# start at left bottom, end at right top
# M - marker
# X - burst
#
#               M
# ^   X X X X X X
# |   X X X X X X
# |   X X X X X X
# |   X X X X X X
# y'  M 
#     x' - - - - >
#
# The pressure changes in x-direction

if n_imprints_x == 1:
	att_step = 0
else:
	att_step = (att_max-att_min)/(n_imprints_x-1)

# attenuatorValues = []
# att_val = att_min
# for i in range(n_imprints_z):
# 	attenuatorValues.append(att_val)
# 	att_val = att_val + att_step # update att_val
attenuatorValues = (0.100, 1.000, 2.000, 3.000, 4.000, 5.000, 6.000,
                    7.000, 8.000, 9.000, 10.000, 10.357, 10.714,
                    11.071, 11.429, 11.786, 12.143, 12.500, 12.857,
                    13.214, 13.571, 13.929, 14.286, 14.643, 15.000) 

################################################################################
# Set Attenuator values here: Units are Torr
#att_min = 3.00
#att_max = 15
#att_step = (att_max-att_min)/(n_imprints_z-1)

#attenuatorValues = []
#att_val = att_min
#for i in range(n_imprints_z):
#	attenuatorValues.append(att_val)
#	att_val = att_val + att_step # update att_val
################################################################################


################################################################################

# define global variables
x_EPICS = ""
y_EPICS = ""
z_EPICS = ""
att_EPICS = ""


################################################################################
#      * * * * * * * *         F U N C T I O N S        * * * * * * * *        #
# Function to translate from sample coordinates to manipulator (LAB) coordinates
# - returns: 3-vector of manipulator x,y,z
def sample_to_manipulator(s_x,s_y,s_z, rotmatrix): 
    sample_vec = np.array([ [s_x],
                            [s_y],
                            [s_z] ])
    manip_vec = (np.dot(rotmatrix, sample_vec)).ravel()
    return manip_vec[0], manip_vec[1], manip_vec[2]

# Function to set attenuator to desired value, wait 'delay' seconds to settle
def set_attenuator(value,delay):
	global att_EPICS
	att_EPICS = "caput GATT:FEE1:310:P_DES " + str(value)
	print "Wait " + str(delay) + "sec for attenuator to settle at " + str(value) + "torr"
	os.system(att_EPICS)
	time.sleep(delay)

# Function to set manipulator at (x,y,z) position
def set_manipulator_xyz(x,y,z, rotmatrix):
	global x_EPICS,y_EPICS,z_EPICS
	# NB: We need to move the sample to the x-ray, which is fixed. Hence
	# we need to send the negative of the manipulator x,y,z 
	manip_vec = sample_to_manipulator(x,y,z, rotmatrix)
	x_EPICS = "caput SXR:EXP:MMS:01 "+str(-manip_vec[0]+manipOrigin_x)
	y_EPICS = "caput SXR:EXP:MMS:02 "+str(-manip_vec[1]+manipOrigin_y)
	z_EPICS = "caput SXR:EXP:MMS:03 "+str(manip_vec[2]+manipOrigin_z)
	os.system(x_EPICS)
	os.system(y_EPICS)
	os.system(z_EPICS)
	print "Wait 2sec for manipulator to settle at ("+str(x)+","+str(y)+","+str(z)+")"
	time.sleep(2) 
	#time.sleep(10) 

# Function to request bursts
def request_burst(n_bursts):
	global x_EPICS,y_EPICS,z_EPICS,att_EPICS
	print "Request burst with " + str(n_bursts) + " FEL shots"
	nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(n_bursts)
	os.system(nFEL_shots_EPICS)
	burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"
	os.system(burst_EPICS)

	print x_EPICS," ",y_EPICS," ",z_EPICS
	print att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
	time.sleep(1.5) # if n_bursts> X than wait ???

    #      * * * * * * * *         F U N C T I O N S        * * * * * * *      #
################################################################################


################################################################################
########################        START OF SCRIPT        #########################
################################################################################
print "\n===================================="
print   "*** Imprint 2D scan IH started ***"
print   "====================================\n"
# T = 0
def make_rot_matrix(x_angle, y_angle, z_angle) :

    # Convert angles from degrees to radians
    x_angle_rad = np.deg2rad(x_angle)
    y_angle_rad = np.deg2rad(y_angle)
    z_angle_rad = np.deg2rad(z_angle)

    # calculate cos(theta) and sin(thera)
    cos_x = np.cos(x_angle_rad)
    sin_x = np.sin(x_angle_rad)

    cos_y = np.cos(y_angle_rad)
    sin_y = np.sin(y_angle_rad)
    
    cos_z = np.cos(z_angle_rad)
    sin_z = np.sin(z_angle_rad)

    # Construct rotation matrices
    Rx = np.array([ [1,     0,      0],
                    [0, cos_x, -sin_x],
                    [0, sin_x,  cos_x] ])                      
    
    Ry = np.array([ [ cos_y, 0, sin_y],
                    [     0, 1,     0],
                    [-sin_x, 0, cos_x] ])                      
    
    Rz = np.array([ [cos_z, -sin_z, 0],
                    [sin_z,  cos_z, 0], 
                    [0,      0,     1] ])                      

    # The 3D rotation matrix R= Rz * Ry * Rx 
    rotmatrix = np.dot(Rz, np.dot(Ry,Rx))

    return rotmatrix
    

# Create rotation matrix
rotmatrix = make_rot_matrix(sampleAngle_x,
                            sampleAngle_y,
                            sampleAngle_z)



#### Mark before scan starts ####
print "Set beginning mark spot"
# Set attenuator
set_attenuator(mark_attenuator,0) # set manually before shooting ???
# T = T + 0
# Set manipulator
set_manipulator_xyz(x_mark_start, y_mark_start, 0.0, rotmatrix)
# Request burst
request_burst(mark_burst)
time.sleep(1)
# T = T + 1.5
######  START SCAN  ######
print "\n====================="
print   "*** Starting scan ***"

# Start position (mm)
xStart = x_mark_start
yStart = y_mark_start + deltaY
#zStart = z_mark_start

xPos = xStart
yPos = yStart
zPos = 0.0
deltaP = 1.0

# Loop over sample x-positions
# Also controls gas-attenuator pressure 
for xStep in range(n_imprints_x) :
    print ""
    # Set Attenuator and wait
	# Waiting time (delay) for setting gas attenuator is dynamic
	# 	For pressure  0 it waits 90sec/tor
	#	For pressure 15 it waits 30sec/tor
    if xStep == 0:
        deltaP = mark_attenuator-attenuatorValues[xStep]
    else:
        deltaP = attenuatorValues[xStep]-attenuatorValues[xStep-1]
    
	if attenuatorValues[xStep-1] >= 1:
		delay = (50-attenuatorValues[xStep]-0.5*deltaP)*deltaP
	else:
		delay = (90-4*attenuatorValues[xStep]-2*deltaP)*deltaP

	set_attenuator(attenuatorValues[xStep],delay)        
	yPos = yStart # Reset y-position
    # T = T + delay
    
	for yStep in range(n_imprints_y):

		# Set manipulator at new position
		set_manipulator_xyz(xPos,yPos,zPos, rotmatrix)
        # T = T + 1.5
		# Request burst
		request_burst(1)   
        # T = T + 1.5
		# Update y-position
		yPos = yPos + deltaY

	# Update x-position
	xPos = xPos + deltaX

print "\n*** Scan finished! ***"
print   "======================\n"

#### Mark after scan ends
print "Set end mark spot"
x_mark_end = xPos - deltaX
y_mark_end = yPos 
#z_mark_end = zPos - deltaZ
z_mark_end = zPos

# Set attenuator
# set_attenuator(mark_attenuator,120)
set_attenuator(mark_attenuator,60)
# Set manipulator
set_manipulator_xyz(x_mark_end,y_mark_end,z_mark_end, rotmatrix)
# Request burst
request_burst(mark_burst)

print "\nDONE!\n"
