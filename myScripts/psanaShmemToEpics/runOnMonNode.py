import psana
from pylab import *
import time
ds = psana.DataSource("shmem=psana.0:stop=no")
#myEvents = enumerate(ds.events())
#nevent,evt = next(myEvents)
#psana.DetNames()
acquiris1Det = psana.Detector("Acq01")
execfile("numpyClientServer.py")

mySize = 2000

toExport = zeros([120,mySize])
#toExportB = array([])
channel_number = 0

for nevent, evt in enumerate(ds.events()):
	#try:
	time.sleep(0.01)
	dummy = acquiris1Det(evt)
	if(dummy is None): continue
	y,x = dummy
	myTime = evt.get(psana.EventId)
	y[channel_number,4720]=myTime.fiducials()
	#numpysocket.startClient("sxr-console",12301,y[2,89100:89600])
	#toExport[int(nevent%120),:] = y[channel_number,4720:5220]
	toExport[int(nevent%120),:] = y[channel_number,4720:4720+mySize]
	#print nevent

	if(nevent%120 == 0): 
		print("test")
		print("Channel Number "+str(channel_number))
		numpysocket.startClient("sxr-console",12301,toExport)
		#numpysocket.startClient("sxr-console",12301,toExportB)
		#toExportB = array([])

	#toExportB = append(toExportB,y[2,89100:89600]) 		

	#except:
	#	break


"""
for nevent, evt in enumerate(ds.events()):
	try:
		time.sleep(0.75)
		y,x = acquiris1Det(evt)
		myTime = evt.get(psana.EventId)
		y[2,89100]=myTime.fiducials()
		numpysocket.startClient("sxr-console",12301,y[2,89100:89600])

		numpysocket.startClient("sxr-console",12301,toExport)

		
	except:
		break
"""
