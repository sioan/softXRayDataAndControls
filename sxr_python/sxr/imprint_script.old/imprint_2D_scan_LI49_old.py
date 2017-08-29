#!/bin/env python

import sys
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
#      x'-axis : perpendicular to sample plane, where x=0 is sample surface
#      y'-axis : parallel to y-axis
#      z'-axis : perpendicular to x' and y'
#                parallel to z-axis at zero-degrees angle
#
# Thus regular grid of imprints has co-ordinates (0, y'_i, z'_i)
################################################################################


################################################################################
#  Sample angle in degrees
#  Defined with respect to z-axis (x-ray direction)
#   - increasing angle defined as moving from z-axis toward positive
#     x-axis  
#   - zero defines sample parallel to z-axis

# sampleAngle = 45.0
sampleAngle = 0.0
################################################################################


################################################################################
# 2D Scan settings : Defined in sample-frame
# Set (y',z') starting position, distance between imprints, and number of imprints  
# Units are in mm
#
# start at left bottom, end at right top
# M - marker
# X - burst
#             M
#   X X X X X X
#   X X X X X X
#   X X X X X X
#   X X X X X X
#   M 

# Number of imprints in (y',z')
n_imprints_y = 10
n_imprints_z = 5

# Start fiducial defined in sample-frame (y',z')
x_mark_start = -6
y_mark_start = -131
z_mark_start = 4.0

# Distance between imprints in (y',z') (mm)
deltaY = -0.2
deltaZ = 0.2*1.4

# Start position (mm)
xStart = x_mark_start
yStart = y_mark_start + deltaY
zStart = z_mark_start

# Number of FEL pulses and attenuator setting for fiducials 
mark_attenuator = 3.00
mark_burst = 100
################################################################################


################################################################################
# Set Attenuator values here: Units are Torr
att_min = 3.00
att_max = 15
att_step = (att_max-att_min)/(n_imprints_z-1)

attenuatorValues = []
att_val = att_min
for i in range(n_imprints_z):
	attenuatorValues.append(att_val)
	att_val = att_val + att_step # update att_val
################################################################################

# define global variables
x_EPICS = ""
y_EPICS = ""
z_EPICS = ""
att_EPICS = ""

################################################################################
# Function to translate from sample coordinates to manipulator (LAB) coordinates
# - returns: 3-vector of manipulator x,y,z
def sample_to_manipulator(s_x,s_y,s_z): 
    sample_vec = np.array([[s_x],[s_z]])
    manip_vec = (np.dot(rotmatrix, sample_vec)).ravel()
    return manip_vec[0],s_y,manip_vec[1]

# Function to set attenuator to desired value, wait 'delay' seconds to settle
def set_attenuator(value,delay):
	global att_EPICS
	att_EPICS = "caput GATT:FEE1:310:P_DES " + str(value)
	print "Wait " + str(delay) + "sec for attenuator to settle at " + str(value) + "torr"
	os.system(att_EPICS)
	time.sleep(delay)

# Function to set manipulator at (x,y,z) position
def set_manipulator_xyz(x,y,z):
	global x_EPICS,y_EPICS,z_EPICS
	# NB: We need to move the sample to the x-ray, which is fixed. Hence
	# we need to send the negative of the manipulator x,y,z 
	manip_vec = sample_to_manipulator(x,y,z)
	x_EPICS = "caput SXR:EXP:MMS:01 "+str(manip_vec[0])
	y_EPICS = "caput SXR:EXP:MMS:02 "+str(manip_vec[1])
	z_EPICS = "caput SXR:EXP:MMS:03 "+str(manip_vec[2])
	os.system(x_EPICS)
	os.system(y_EPICS)
	os.system(z_EPICS)
	print "Wait 2sec for manipulator to settle at ("+str(x)+","+str(y)+","+str(z)+")"
	time.sleep(2) 

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
	
################################################################################


################################################################################
########################        START OF SCRIPT        #########################
################################################################################
print "\n===================================="
print   "*** Imprint 2D scan LI49 started ***"
print   "====================================\n"

# Convert from degrees to radians
sampleAngleRad = np.deg2rad(sampleAngle)

# Calculate cos(theta) and sin(theta)
cos_theta = np.cos(sampleAngleRad)
sin_theta = np.sin(sampleAngleRad)

# Define rotation matrix
rotmatrix = np.array([[cos_theta,sin_theta],[-sin_theta,cos_theta]])

#### Mark before scan starts ####
print "Set beginning mark spot"

# Set attenuator
set_attenuator(mark_attenuator,0) # set manually before shooting ???
# set_attenuator(mark_attenuator,5) # set manually before shooting ???
# Set manipulator
set_manipulator_xyz(x_mark_start,y_mark_start,z_mark_start)
# Request burst
request_burst(mark_burst)

######  START SCAN  ######
print "\n====================="
print   "*** Starting scan ***"

xPos = xStart
zPos = zStart
for zStep in range(n_imprints_z) :
	print ""
	# Set Attenuator
	if zStep == 0:
		# set_attenuator(attenuatorValues[zStep],60)
		if attenuatorValues[zStep] != mark_attenuator:
			set_attenuator(attenuatorValues[zStep],60)
	else:
		# set_attenuator(attenuatorValues[zStep],25)
		set_attenuator(attenuatorValues[zStep],40)

	yPos = yStart # Reset y-position
	for yStep in range(n_imprints_y):

		# Set manipulator at new position
		set_manipulator_xyz(xPos,yPos,zPos)
		# Request burst
		request_burst(1)   
		# Update y-position
		yPos = yPos + deltaY

	# Update z-position
	zPos = zPos + deltaZ

print "\n*** Scan finished! ***"
print   "======================\n"

#### Mark after scan ends
print "Set end mark spot"
x_mark_end = xPos
y_mark_end = yPos
z_mark_end = zPos - deltaZ

# Set attenuator
# set_attenuator(mark_attenuator,120)
set_attenuator(mark_attenuator,60)
# Set manipulator
set_manipulator_xyz(x_mark_end,y_mark_end,z_mark_end)
# Request burst
request_burst(mark_burst)

print "\nDONE!\n"
