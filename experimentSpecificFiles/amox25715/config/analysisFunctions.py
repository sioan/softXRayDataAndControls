from pylab import *
import psana
import IPython
import h5py
import numpy
import scipy.ndimage as im
import scipy.misc as misc

def peakFinding(detectorObject,thisEvent):
	
	detectorName = detectorObject['self_name']
	img = detectorObject[detectorName].image(thisEvent)
	myDict = {}
	myDict['peakCoordinate'] = zeros(20000)-1

	
	if (img is None):
		return myDict

	if (img.sum()):
		#imgcnt+=1
		thr1 = np.max([min(img.max(0)), min(img.max(1))])
		img = im.median_filter(img, (3,3))		
		img = img * (img > thr1)
		
		#peaks = alg.peak_finder_v4(img, thr_low=5, thr_high=10, rank=4, r0=5, dr=0.05)
		#cent0.append(np.transpose(np.array([peaks[:,2],peaks[:,1]])))

		if (img.sum()):	
		
			cent = []
			#ele_energy.append([nevent,ebeam.ebeamL3Energy()])
			img = im.gaussian_filter(img,1.3)  
			img = img * (img > 0.85*thr1)
		
			edge = 5
			a,b = np.nonzero(img[edge:img.shape[0]-edge,edge:img.shape[1]-edge])
			a = a + edge
			b = b + edge
			if (len(a)>0):
				for i in xrange(len(a)):
					if ((img[a[i],b[i]]>img[a[i]-1,b[i]]) and (img[a[i],b[i]]>img[a[i],b[i]-1]) and (img[a[i],b[i]]>=img[a[i]+1,b[i]]) and (img[a[i],b[i]]>=img[a[i],b[i]+1]) and
					(img[a[i],b[i]]>img[a[i]-1,b[i]-1]) and (img[a[i],b[i]]>img[a[i]-1,b[i]+1]) and (img[a[i],b[i]]>=img[a[i]+1,b[i]-1]) and (img[a[i],b[i]]>=img[a[i]+1,b[i]+1])):
						cent.extend([b[i],a[i]])#saves b-x, a-y coordinates

		myDict['peakCoordinate'] = cent
		myDict['peakCoordinate'] = append(myDict['peakCoordinate'],zeros(20000-len(myDict['peakCoordinate'])))

	return myDict

def integrateAcqiris(detectorObject,thisEvent):
	myDict = {}
	AcqAlias = detectorObject['self_name']	
	y,x = detectorObject[AcqAlias](thisEvent)
	

	if (None is y):
		myDict['MCP'] = -99999.0
	else:
		myDict['MCP'] = sum(y[0,4720:5220]-mean(y[0,0:4000]))
				
	

	return myDict

def chopperState(detectorObject,thisEvent):
	myDict = {}
	chopperAlias = detectorObject['self_name']
	y,x = detectorObject[chopperAlias](thisEvent)

	if (None is y):
		myDict['chopperState']=-999999.0
	else:
		myDict['chopperState']= mean(y[0])	#justify with boiler plate view analysis. this is painful. how to streamline?
		#idea: put a commented flag here that tells the "to be written" script to bring up data

	return myDict

def genericReturn(detectorObject,thisEvent):
	myDict = {}
	genericDetectorAlias = detectorObject['self_name']
	genericValue = detectorObject[genericDetectorAlias](thisEvent)
	
	if(genericValue is None):
		myDict[genericDetectorAlias] = -9999.0
		
	else:
		myDict[genericDetectorAlias] = genericValue

	return myDict

def getGMD(detectorObject, thisEvent):
	myAlias = detectorObject['self_name']
	temp = detectorObject[myAlias].get(thisEvent)
	myDict = {}
	if(temp is None):

		myDict['milliJoulesPerPulse'] = -99999.0
	else:
		myGmdValue = temp.milliJoulesPerPulse()
		myDict['milliJoulesPerPulse'] = myGmdValue

	return myDict


def regressAgainstAverageWave(detectorObject,thisEvent):
	selfName = detectorObject['self_name']

	myDict = {}
	myDict['amplitude'] = -99999.0
	if None is detectorObject[selfName](thisEvent):
		pass

	else:
		myWaveForm = -detectorObject[selfName](thisEvent)[0][0]
		myWaveForm-=mean(myWaveForm)

		myDict['amplitude'] = dot(myWaveForm,referenceWave)/refWaveSelfDot

	return myDict

def getPeak(detectorObject,thisEvent):

	selfName = detectorObject['self_name']

	myWaveForm = -detectorObject[selfName](thisEvent)[0][0]

	myWaveForm -= mean(myWaveForm[-1000:-100])

	x = arange(len(myWaveForm))[7500:10000]-8406
	myFit = polyfit(x, myWaveForm[7500:10000],3)

	p = poly1d(myFit)
	myMax = max(p(x))

	#return myFit[-1]	#placing a dictionary here also works
	return myMax	

def accumulateAverageWave(detectorObject,thisEvent,previousProcessing):

	selfName = detectorObject['self_name']

	#IPython.embed()

	if('averageWave0' not in previousProcessing):
		print ("initializing accumulator")
		previousProcessing['averageWave0']=0.0
		previousProcessing['averageWave1']=0.0

	myWaveForm0 = -detectorObject[selfName](thisEvent)[0][0]
	myWaveForm0 -= mean(myWaveForm0[:2500])

	myWaveForm1 = -detectorObject[selfName](thisEvent)[0][1]
	myWaveForm1 -= mean(myWaveForm1[:2500])

	previousProcessing['averageWave0'] = (previousProcessing['averageWave0']+myWaveForm0)
	previousProcessing['averageWave1'] = (previousProcessing['averageWave1']+myWaveForm1)

	return previousProcessing

def getWaveForm(detectorObject,thisEvent):

	selfName = detectorObject['self_name']

	if (None not in [detectorObject[selfName](thisEvent)[0][0]]):
		return detectorObject[selfName](thisEvent)[0][0]
	else:	
		return 0
	
def get(detectorObject,thisEvent):
	if (None not in [detectorObject(thisEvent)]):
		return detectorObject(thisEvent)
	else:
		return 0

def getRaw(detectorObject,thisEvent):
	if (None not in [detectorObject(thisEvent)]):
		return detectorObject(thisEvent)
	else:
		return 0

#def getGMD(detectorObject,thisEvent):
#	temp = detectorObject.get(thisEvent)
#	if (None not in [temp]):
#		return temp.milliJoulesPerPulse()
#	else: 	
#		return 0

def getEBeam(detectorObject,thisEvent):
	temp = detectorObject.get(thisEvent)
	if(None not in [temp]):
		return temp.ebeamPhotonEnergy()
	else:
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

