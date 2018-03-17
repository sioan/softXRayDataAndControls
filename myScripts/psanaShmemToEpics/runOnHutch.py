#need to source psana
#go to the  pyepics on sioan desktop  and run this using execfile("/reg/neh/home/sioan/Desktop/upComingExperiments/LQ76/runOnSXR.py")
import sys
sys.path.append('/reg/neh/home/sioan/Desktop/pyepics-3.2.5')
import epics
import argparse
from pylab import *
from  numpyClientServer import *
#execfile("/reg/neh/home/sioan/Desktop/pyepics-3.2.5/numpyClientServer.py")
import time

parser = argparse.ArgumentParser(description='Serve as numpy array server for shmem -> EPICS pipeline. Run on a hutch control machine.')
parser.add_argument('hutch', metavar='HUTCH', help='Name of hutch (AMO or SXR)')
try:
	args=parser.parse_args()
except:
	pass #Likely no arguments passed in
if args.hutch.lower() == "amo":
	notepv = "AMO:NOTE:ARRAYB:01"
elif args.hutch.lower() == "sxr":
	notepv = "SXR:NOTE:ARRAYB:01"
else:
	print "Error, hutch %s not supported!" % args.hutch
        sys.exit()

while(True):
	time.sleep(.05)
	print("test")
	try:
		myData = numpysocket.startServer(12301)
		for i in arange(120):
			time.sleep(.04)
			epics.caput(notepv, myData[i])
		
	
	except:
		break
"""
while(True):
	time.sleep(1)
	try:
		myData = numpysocket.startServer(12301)
		epics.caput("DAQ:SXR:MON:ACQ13:Waveform",myData[i])
			
	
	except:
		break
"""
