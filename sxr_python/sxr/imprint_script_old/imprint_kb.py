#!/bin/env python
"""
imprint_kb.py

Usage:
  imprint_kb.py [--config=cfg] [--burst [-f]] [--verbose]
  imprint_kb.py [-h | --help]

Options:
  -h|--help     Show this help message
  --config=cfg  Path to the configuration file that will be used
                for the positions. [default: imprint_configurations/imprint_kb_standard.cfg]
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



def imprintKB(config_file_name, Burst = False, verbose = False):
	# Create the parser object
	parser = SafeConfigParser()
	parser.read(config_file_name)

	# X Y Positions
	xfrom = float(parser.get("positions", "xfrom"))
	deltaX = float(parser.get("positions", "deltaX"))
	yfrom = float(parser.get("positions", "yfrom"))
	deltaY = float(parser.get("positions", "deltaY"))

	nPoints = int(parser.get("positions", "nPoints"))

	# KB Positions
	kb11 = float(parser.get("kb", "kb11"))
	kb12 = float(parser.get("kb", "kb12"))
	kb13 = float(parser.get("kb", "kb13"))
	kb14 = float(parser.get("kb", "kb14"))

	kb11s = float(eval(parser.get("kb", "kb11s")))
	kb12s = float(eval(parser.get("kb", "kb12s")))
	kb13s = float(eval(parser.get("kb", "kb13s")))
	kb14s = float(eval(parser.get("kb", "kb14s")))

	# PVs
	PV_X = parser.get("PVs", "PV_X")
	PV_Y = parser.get("PVs", "PV_Y")

	PV_kb11 = parser.get("PVs", "PV_kb11")
	PV_kb12 = parser.get("PVs", "PV_kb12")
	PV_kb13 = parser.get("PVs", "PV_kb13")
	PV_kb14 = parser.get("PVs", "PV_kb14")

	if verbose:		
		print "\nInitial X position: {0}. Delta X: {0}".format(xfrom, deltaX)
		print "Initial Y position: {0}. Delta Y: {0}".format(yfrom, deltaY)

		print "\nKB11: {0}. KB11s: {0}".format(kb11, kb11s)
		print "KB12: {0}. KB12s: {0}".format(kb12, kb12s)
		print "KB13: {0}. KB13s: {0}".format(kb13, kb13s)
		print "KB14: {0}. KB14s: {0}".format(kb14, kb14s)

		print "\nX Motor PV: {0}".format(PV_X)
		print "Y Motor PV: {0}".format(PV_Y)

		print "\nKB11 PV: {0}".format(PV_kb11)
		print "KB12 PV: {0}".format(PV_kb12)
		print "KB13 PV: {0}".format(PV_kb13)
		print "KB14 PV: {0}".format(PV_kb14)

		print "\nNumber of points: {0}".format(nPoints)

	yPos = yfrom
	xPos = xfrom


	# Create Motor Objects
	motor_X = epics_ims_motor(PV_X)
	motor_Y = epics_ims_motor(PV_Y)

	motor_kb11 = epics_ims_motor(PV_kb11)
	motor_kb12 = epics_ims_motor(PV_kb12)
	motor_kb13 = epics_ims_motor(PV_kb13)
	motor_kb14 = epics_ims_motor(PV_kb14)

	# Move the kb motors to starting position
	motor_kb11.mv(kb11)
	motor_kb12.mv(kb12)
	motor_kb13.mv(kb13)
	motor_kb14.mv(kb14)

	# Wait for them to finish moving before beginning
	motor_kb11.wait_for_motion()
	motor_kb12.wait_for_motion()
	motor_kb13.wait_for_motion()
	motor_kb14.wait_for_motion()

	if verbose: print "Beginning imprint routine..."
	for yStep in range(nPoints):

		yPos += deltaY
		kb13_mv = kb13+(kb13s*(yStep-((nPoints-1)/2)))
		kb14_mv = kb14+(kb14s*(yStep-((nPoints-1)/2)))

		if verbose:
			print "\nMoving Y to {0}".format(yPos)
			print "Moving KB13 to {0}".format(kb13_mv)
			print "Moving KB14 to {0}".format(kb14_mv)
		# Move kb13, kb14, and Y then wait for them to finish
		motor_kb13.mv(kb13_mv)
		motor_kb14.mv(kb14_mv)
		motor_Y.mv(yPos)

		if verbose: 
			print "Waiting for motors to finish motion..."		
		motor_kb13.wait_for_motion()
		motor_kb14.wait_for_motion()
		motor_Y.wait_for_motion()

		for xStep in range(nPoints):
			
			xPos += deltaX
			kb11_mv = kb11+(kb11s*(xStep-((nPoints-1)/2)))
			kb12_mv = kb12+(kb12s*(xStep-((nPoints-1)/2)))
			
			if verbose:
				print "\nMoving X to {0}".format(xPos)
				print "Moving KB11 to {0}".format(kb11_mv)
				print "Moving KB12 to {0}".format(kb12_mv)
			# Move kb11, kb12, and X then wait for them to finish
			motor_kb11.mv(kb11_mv)
			motor_kb12.mv(kb12_mv)
			motor_X.mv(xPos)

			if verbose: 
				print "Waiting for motors to finish motion..."		
			motor_kb11.wait_for_motion()
			motor_kb12.wait_for_motion()
			motor_X.wait_for_motion()

			# Request burst if Burst is True
			if Burst:
				if verbose:
					print "Request burst"
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

	# The actual function 
	imprintKB(arguments["--config"],
	          arguments["--burst"],
	          arguments["--verbose"])
