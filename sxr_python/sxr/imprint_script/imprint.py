#!/bin/env python
"""
imprint.py

Usage:
  imprint.py [--config=cfg] [--burst [-f]] [--verbose]
  imprint.py [-h | --help]

Options:
  -h|--help     Show this help message
  --config=cfg  Path to the configuration file that will be used
                for the positions. [default: imprint_configurations/imprint_standard.cfg]
  --burst       Fires a burst. Will prompt to make sure. Use -f to overide check
  --verbose     Print more info on active process

"""

import sys
import os
import time

from pprint import pprint
from ConfigParser import SafeConfigParser
from sxr_common.epics_ims_motor import epics_ims_motor
from docopt import docopt


def imprint(config_file_name, Burst = False, verbose = False):
	# Create the parser object
	parser = SafeConfigParser()
	parser.read(config_file_name)

	# Grab all the positions casted as floats
	xfrom = float(parser.get("positions", "xfrom"))
	deltaX = float(parser.get("positions", "deltaX"))
	yfrom = float(parser.get("positions", "yfrom"))
	deltaY = float(parser.get("positions", "deltaY"))
	
	attenuatorString = parser.get("positions", "attenuatorValues")
	attenuatorValues = [float(x) for x in attenuatorString.split()]


	# Range Values for the motors
	xRange = int(parser.get("range", "xRange"))
	yRange = int(parser.get("range", "yRange"))


	# Get the PVs
	attenuatorPV = parser.get("PVs", "PV_Attenuator")
	PV_X = parser.get("PVs", "PV_X")
	PV_Y = parser.get("PVs", "PV_Y")


	# Parsing Check
	if verbose:
		print "\nInitial X position: {0}. Delta X: {0}".format(xfrom, deltaX)
		print "Initial Y position: {0}. Delta Y: {0}".format(yfrom, deltaY)

		print "\nAll attenuator Values:\n", attenuatorValues 

		print "\nRange X: {0}. Range Y: {0}.".format(xRange, yRange)

		print "\nX Motor PV: {0}".format(PV_X)
		print "Y Motor PV: {0}".format(PV_Y)
		print "Attenuator PV: {0}".format(attenuatorPV)


	# Define start values for x and y
	yPos = yfrom
	xPos = xfrom


	# Not a motor, use the code from the old version

	motor_X = epics_ims_motor(PV_X)
	motor_Y = epics_ims_motor(PV_Y)

	for yStep in range(yRange):

	    yPos -= deltaY                    #See Config notes
	    
	    if verbose: 
	        print "\nMoving Y to {0}".format(yPos)
	        print "Moving attenuator to {0}".format(attenuatorValues[yStep])
	    motor_Y.mv(yPos)
	    motor_Attenuator.mv(attenuatorValues[yStep])

	    # Set Attenuator
	    att_EPICS=  "caput " + attenuatorPV +str(attenuatorValues[yStep])
	    print "wait for attenuator to settle"
	    os.system(att_EPICS)
	    time.sleep(20)

	    if verbose: 
	        print "Wait for attenuator to settle"
	    motor_Y.wait_for_motion()
	    motor_Attenuator.wait_for_motion()

	    for xStep in range(xRange):

	        xPos += deltaX

	        if verbose:
	            print "Moving X to {0}".format(xPos)
	        # Set x motor
	        motor_X.mv(xPos)
	        motor_X.wait_for_motion()

	        # Request burst
	        if Burst:
	            if verbose:
	                print "Request burst"
	            This is commented out because it will fire the FEL if it runs
	            burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"
	            os.system(burst_EPICS)
	            time.sleep(1) 

	    xPos = xfrom


	print "\nDONE!"


if __name__ == "__main__":

	arguments = docopt(__doc__)
	
	# Make sure burst is deliberately on. To skip this prompt, enter -f with the
	# --burst option
	if arguments["--burst"] and not arguments["-f"]:
		print "Burst mode selected."
		answer = raw_input("Are you sure? [y/n] ")

		while answer is not 'y' and answer is not 'n':
			answer = raw_input("Please enter y or n: ")
		
		if answer == "n":
			if arguments["--verbose"]: print "Changing burst to false"
			arguments["--burst"] == False

	if arguments["--verbose"]:
		print "\nConfig to be used: {0}".format(arguments["--config"])
		if arguments["--burst"]: print "Burst mode activated"
		else: print "Burst mode deactivated"

	
	imprint(arguments["--config"],
	        arguments["--burst"],
	        arguments["--verbose"])
