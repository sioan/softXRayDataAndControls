#need to source psana
#go to the  pyepics on sioan desktop  and run this using execfile("/reg/neh/home/sioan/Desktop/upComingExperiments/LQ76/runOnSXR.py")
import sys
sys.path.append('/reg/neh/home/sioan/Desktop/pyepics-3.2.5')
import epics
from pylab import *
from  numpyClientServer import *
#execfile("/reg/neh/home/sioan/Desktop/pyepics-3.2.5/numpyClientServer.py")
import time


while(True):
	time.sleep(.05)
	try:
		myData = numpysocket.startServer(12301)
		for i in arange(120):
			time.sleep(.04)
			epics.caput("SXR:NOTE:ARRAY:01",myData[i])
		
	
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
