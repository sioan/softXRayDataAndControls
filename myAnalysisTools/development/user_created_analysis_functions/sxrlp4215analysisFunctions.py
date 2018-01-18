from pylab import *
import h5py
import psana
import IPython

# from averagePulse import *


# averagePulseInstance = averagePulse('ref.h5')


def genericReturn(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	return detectorObject[selfName](thisEvent)


def genericSummaryZero(detectorObject,thisEvent,previousProcessing):
	return 0


def myZeroReturn(detectorObject,thisEvent,previousProcessing):
	return 0


def getTimeToolData(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	ttData = detectorObject[selfName].process(thisEvent)
	myDict = {}	
	if(ttData is None):
		
		myDict['amplitude'] = -99999
		myDict['pixelTime'] = -99999
		myDict['positionFWHM'] = -99999
	else:

		myDict['amplitude'] = ttData.amplitude()
		myDict['pixelTime'] = ttData.position_time()
		myDict['positionFWHM'] = ttData.position_fwhm()

	return myDict

# bsub -n 16 -o myoutput%J.log -q psnehhiprioq mpirun python psanaXtcDataExtractor.py -e sxrlp4215 -r 183

def getDelay(detectorObject, thisEvent):
	selfName = detectorObject['self_name']

	# IPython.embed()

	if detectorObject[selfName].values(thisEvent) is None:
		myDictionary = {'DLS_PS': -999.0}
		return myDictionary

	DLS_PS = detectorObject[selfName].values(thisEvent)[0]
	return {'DLS_PS': DLS_PS}


def getPeakArea(detectorObject, thisEvent):
	selfName = detectorObject['self_name']

	if detectorObject[selfName](thisEvent) is None:
		myDictionary = {'trace': -999.0 * np.ones(200, dtype=np.float64), 'even_level': -999.0, 'odd_level': -999.0, 'pulse_area': -999.0}
		# 243 myDictionary = {'trace': -999.0 * np.ones(2000, dtype=np.float64), 'even_level': -999.0, 'odd_level': -999.0,
		# 				'pulse_area': -999.0}
		return myDictionary

	# evenAverage = averagePulseInstance.f['summary/nonMeaningfulCoreNumber0/APD/averageWave1']
	# oddAverage = averagePulseInstance.f['summary/nonMeaningfulCoreNumber0/APD/averageWave2']
	# n = averagePulseInstance.f['summary/nonMeaningfulCoreNumber0/APD/n']

	#traces = detectorObject[selfName](thisEvent)[0][3] #243 - laser diode
	traces = detectorObject[selfName](thisEvent)[0][1] #< 243 - APD 4mm


	even_level = mean(traces[8000:-6:2])
	odd_level = mean(traces[8001:-6:2])
	#even_level = mean(traces[12000:-6:2])
	#odd_level = mean(traces[12001:-6:2])

	even_trace = -traces[1160:1360:2] + even_level
	odd_trace = -traces[1161:1361:2] + odd_level
	# even_trace = traces[1000:3000:2] - even_level
	# odd_trace = traces[1001:3001:2] - odd_level

	iw_trace = np.zeros(even_trace.shape[0] * 2, dtype=np.float64)
	iw_trace[::2] = even_trace
	iw_trace[1::2] = odd_trace

	pulse_area = np.sum(iw_trace)

	myDictionary = {'trace': traces[1160:1360], 'even_level': even_level, 'odd_level': odd_level, 'pulse_area': pulse_area}
	# myDictionary = {'trace': traces[1000:3000], 'even_level': even_level, 'odd_level': odd_level,
	# 				'pulse_area': pulse_area}

	# IPython.embed()

	return myDictionary


def getPeak(detectorObject, thisEvent):
	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[:2500])

	x = arange(len(myWaveForm))[7500:10000]-8406
	myFit = polyfit(x, myWaveForm[7500:10000],3)

	p = poly1d(myFit)
	myMax = max(p(x))

	#return myFit[-1]	#placing a dictionary here also works
	return myMax	


def accumulateAverageWave(detectorObject, thisEvent, previousProcessing):
	selfName = detectorObject['self_name']

	# IPython.embed()

	if ('averageWave1' not in previousProcessing):
		print ("initializing accumulator")
		previousProcessing['averageWave1'] = 0.0
		previousProcessing['averageWave2'] = 0.0
		previousProcessing['n'] = 0
	# if ('averageWave2' not in previousProcessing):
	# 	print ("initializing accumulator")
	# 	previousProcessing['averageWave2'] = 0.0

	myWaveForm1 = -detectorObject[selfName](thisEvent)[0][1][0::2]
	myWaveForm2 = -detectorObject[selfName](thisEvent)[0][1][1::2]
	# myWaveForm1 -= mean(myWaveForm1[:2500])

	# Those are in 'summary/nonMeaningfulCoreNumber0/APD/averageWave1'!!
	# Those are in 'summary/nonMeaningfulCoreNumber0/APD/averageWave2'!!
	previousProcessing['averageWave1'] = (previousProcessing['averageWave1'] + myWaveForm1)
	previousProcessing['averageWave2'] = (previousProcessing['averageWave2'] + myWaveForm2)
	previousProcessing['n'] += 1

	return previousProcessing

def getWaveForm(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)[0][0]]):
		return detectorObject[selfName](thisEvent)[0][0]
	else:	
		return 0
	
def get(detectorObject,thisEvent):
	selfName = detectorObject['self_name']
	
	if (None not in [detectorObject[selfName](thisEvent)]):
		return detectorObject[selfName](thisEvent)
	else:
		return 0

def getRaw(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)]):
		return detectorObject[selfName](thisEvent)
	else:
		return 0

def getGMD(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	gmdEvent = detectorObject[selfName].get(thisEvent)
	if (None not in [gmdEvent]):
		return gmdEvent.sumAllPeaksFiltBkgd()
	else: 	
		return -999.0

def getEBeam(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	temp = detectorObject[selfName].get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
		return 0



