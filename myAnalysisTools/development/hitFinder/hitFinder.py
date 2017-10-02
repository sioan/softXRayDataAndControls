from mpi4py import MPI
myComm = MPI.COMM_WORLD
myRank = myComm.Get_rank()
maxRank = myComm.Get_size()

print("my rank = "+str(myRank))
print("max rank = "+str(maxRank))

import numpyClientServer
import psana
from pylab import *

displayServerName = "sxr-console"
myThreshold = 1e6
basePortNumber = 13000

#psana.setOption('psana.calib-dir','/reg//d/psdm/sxr/sxrx22915/calib')
myDataSource = psana.DataSource("shmem=psana.0:stop=no")

myEnumeratedEvents = enumerate(myDataSource.events())

#pnccdDetectorObject = psana.Detector('pnccdFront')
acqirisDetectorObject = psana.Detector("Acq02")

for eventNumber,thisEvent in myEnumeratedEvents:
	if(eventNumber%maxRank)!=myRank: continue

	#myImage = pnccdDetectorObject.image(thisEvent)
	myImage = acqirisDetectorObject.image(thisEvent)[0][0]

	if myImage is None: continue

	if(sum(myImage)>myThreshold):
		numpysocket.startClient(displayServerName,basePortNumber+myRank,myImage)
		#send images and hit rate
