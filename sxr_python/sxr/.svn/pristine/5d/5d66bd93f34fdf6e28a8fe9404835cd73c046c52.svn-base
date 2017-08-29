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



xfrom = 11.5
deltaX = 0.1


yfrom = -0.5
deltaY = 0.1

yPos = yfrom
xPos = xfrom

# kb11 = -.122
# kb12 = -.095
# kb13 = -.094
# kb14 = -.003

kb11 = 0.072
kb12 = 0.22
kb13 = 0.08
kb14 = 0.0467

# kb11s = 0.011
# kb12s = 0.033
# kb13s = 0.043
# kb14s = 0.013

kb11s =1.5 * 0.0036
kb12s =1.5 * 0.011
kb13s =1.5 * 0.0143
kb14s =1.5 * 0.0043

npoints = 7

#kb11 = 4 * 0.072  
#kb12 = 4 * 0.011
#kb13 = 4 * 0.0143
#kb14 = 4 * 0.0043



kb11_EPICS = "caput AMO:KBO:MMS:11.VAL "+str(kb11)
kb12_EPICS = "caput AMO:KBO:MMS:12.VAL "+str(kb12)
kb13_EPICS = "caput AMO:KBO:MMS:13.VAL "+str(kb13)
kb14_EPICS = "caput AMO:KBO:MMS:14.VAL "+str(kb14)

os.system(kb11_EPICS)
os.system(kb12_EPICS)
os.system(kb13_EPICS)
os.system(kb14_EPICS)
time.sleep(3)


for yStep in range(npoints):

    yPos = yPos + deltaY
    kb13_EPICS = "caput AMO:KBO:MMS:13.VAL "+str(kb13+(kb13s*(yStep-((npoints-1)/2))))
    kb14_EPICS = "caput AMO:KBO:MMS:14.VAL "+str(kb14+(kb14s*(yStep-((npoints-1)/2))))
    
    os.system(kb13_EPICS)
    os.system(kb14_EPICS)        

    # Set y motor
    y_EPICS = "caput AMO:LMP:MXM:06:ABSPOSITIONSET "+str(yPos)
    os.system(y_EPICS)
    time.sleep(2)

    for xStep in range(npoints):
        xPos = xPos + deltaX

        kb11_EPICS = "caput AMO:KBO:MMS:11.VAL "+str(kb11+(kb11s*(xStep-((npoints-1)/2))))        
        kb12_EPICS = "caput AMO:KBO:MMS:12.VAL "+str(kb12+(kb12s*(xStep-((npoints-1)/2))))

        os.system(kb11_EPICS)
        os.system(kb12_EPICS)

        # Set x motor
        x_EPICS = "caput AMO:LMP:MXM:05:ABSPOSITIONSET "+str(xPos)
        os.system(x_EPICS)
          
        time.sleep(2)        

        # Request burst
        print "Request burst"
        burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"
        os.system(burst_EPICS)
            
        print x_EPICS," \n", y_EPICS," \n", kb11_EPICS, " \n", kb12_EPICS, " \n", kb13_EPICS, " \n", kb14_EPICS, " \n", burst_EPICS, "******\n"
        time.sleep(1)        

    xPos = xfrom


print "DONE!"







