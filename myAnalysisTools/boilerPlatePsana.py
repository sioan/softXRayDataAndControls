################
#add functionality to take exp, run and event start number as arguments and bring into a interactive python environment.
#how to make ipython friendly?

###########

from pylab import *
import psana
from ImgAlgos.PyAlgos import photons
from scipy.signal import convolve2d
import TimeTool


ttOptions = TimeTool.AnalyzeOptions(get_key='TSS_OPAL',eventcode_nobeam = 162)
ttAnalyze = TimeTool.PyAnalyze(ttOptions)

#runNum = sys.argv[1]
runNum = "38"

#ds = psana.DataSource('exp=xpptut15:run=340')	#test data from AMO runs 10, 15, and 19
#ds = psana.DataSource('exp=sxrm2316:run=103')	#real data from specified experiment (sxrm2316)
#ds = psana.DataSource('exp=sxrlq7615:run='+runNum)
#ds = psana.MPIDataSource('exp=sxrlq7615:run='+runNum+':smd')
#ds = psana.MPIDataSource('exp=sxrlq7615:run='+runNum+':smd')
#ds = psana.MPIDataSource('exp=xpptut15:run='+str(runNum))
#myDataSource = psana.MPIDataSource('exp=sxrk3016:run=118:smd')
#myDataSource = psana.MPIDataSource('exp=sxr10116:run=73:smd')
#myDataSource = psana.MPIDataSource('exp=sxri0414:run=60:smd',module=ttAnalyze)
myDataSource = psana.MPIDataSource('exp=amolp0515:run=105:smd',module=ttAnalyze)
myDataSource = psana.MPIDataSource('exp=sxrlp2615:run=6:smd')


#psana.DetNames()
acqirisDetectorObject = psana.Detector("Acq02")

andorDetectorObject = psana.Detector('andor')

pnccdDetectorObject = psana.Detector('pnccdFront')

tssOpalDetectorObject = psana.Detector('TSS_OPAL')

myEnumeratedEvents = enumerate(myDataSource.events())

for eventNumber,thisEvent in myEnumeratedEvents:
	ttResults = ttAnalyze.process(thisEvent)	
	print eventNumber
	if eventNumber > 200:
		break


eventNumber,thisEvent = next(myEnumeratedEvents)

myWaveform = acqirisDetectorObject(thisEvent)

myImage = andorDetectorObject.image(thisEvent)

ttResults = ttAnalyze.process(thisEvent)

##################################################
###############making a photon image#############
myImage = pnccdDetectorObject.image(thisEvent)

#or 
photonImage = pnccdDetectorObject.photons(thisEvent,adu_per_photon=600)

photonImage = pnccdDetectorObject.image(thisEvent,photonImage)
