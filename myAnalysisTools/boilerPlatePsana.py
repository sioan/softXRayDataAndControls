from pylab import *
import psana
from ImgAlgos.PyAlgos import photons
from scipy.signal import convolve2d

#runNum = sys.argv[1]
runNum = "38"

#ds = psana.DataSource('exp=xpptut15:run=340')	#test data from AMO runs 10, 15, and 19
#ds = psana.DataSource('exp=sxrm2316:run=103')	#real data from specified experiment (sxrm2316)
#ds = psana.DataSource('exp=sxrlq7615:run='+runNum)
#ds = psana.MPIDataSource('exp=sxrlq7615:run='+runNum+':smd')
#ds = psana.MPIDataSource('exp=sxrlq7615:run='+runNum+':smd')
#ds = psana.MPIDataSource('exp=xpptut15:run='+str(runNum))
#myDataSource = psana.MPIDataSource('exp=sxrk3016:run=118:smd')
myDataSource = psana.MPIDataSource('exp=sxr10116:run=73:smd')

#psana.DetNames()
acqirisDetectorObject = psana.Detector("Acq02")

andorDetectorObject = psana.Detector('andor')

pnccdDetectorObject = psana.Detector('pnccdFront')

myEnumeratedEvents = enumerate(myDataSource.events())

eventNumber,thisEvent = next(myEnumeratedEvents)

myWaveform = acqirisDetectorObject(thisEvent)

myImage = andorDetectorObject.image(thisEvent)

##################################################
###############making a photon image#############
myImage = pnccdDetectorObject.image(thisEvent)

#or 
photonImage = pnccdDetectorObject.photons(thisEvent,adu_per_photon=600)

photonImage = pnccdDetectorObject.image(thisEvent,photonImage)
