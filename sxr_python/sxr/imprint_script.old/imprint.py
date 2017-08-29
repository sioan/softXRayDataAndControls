#!/bin/env python
import sys

#from numpy import *
import os
#import getopt
import time
#import traceback
#from princeton import MccBurst, PrincetonDaqMultipleShot

#import pyca
#from Pv import Pv
#import threading



xfrom = 8.80
deltaX = 0.110


yfrom = 4.19

deltaY = 0.150

yPos = yfrom
xPos = xfrom


attenuatorValues = (3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.25, 6.5, 6.75, 7.0, \
                    7.25, 7.5, 7.75, 8.0, 8.25, 8.5, 8.75, 
                    9.25, 9.5, 9.75, 10.0, 10.25, 10.5, 10.75,11.0 )


for yStep in range(26):

    yPos = yPos - 0.15
 
     # Set Attenuator
    att_EPICS=  "caput GATT:FEE1:310:P_DES "+str(attenuatorValues[yStep])
    print "wait for attenuator to settle"
    os.system(att_EPICS)
    time.sleep(20)

    for xStep in range(4):
        
        xPos = xPos + 0.11

        # Set x motor
        x_EPICS = "caput AMO:LMP:MXM:05:ABSPOSITIONSET "+str(xPos)
        os.system(x_EPICS)

        # Set y motor
        y_EPICS = "caput AMO:LMP:MXM:06:ABSPOSITIONSET "+str(yPos)
        os.system(y_EPICS)

        # Set Attenuator
        #att_EPICS=  "caput GATT:FEE1:310:P_DES "+str(attenuatorValues[yStep])
        #print "wait for attenuator to settle"
        #os.system(att_EPICS)
        time.sleep(2)

        # Request burst
        print "Request burst"
        burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"
        os.system(burst_EPICS)
     
        print x_EPICS," ", y_EPICS," ", att_EPICS, " ",burst_EPICS
        time.sleep(1)        

    xPos = xfrom


print "DONE!"







