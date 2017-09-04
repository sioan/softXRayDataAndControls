from pylab import *
import h5py
import pickle

runNumber = 60
f = h5py.File("run"+str(runNumber)+".h5")

#['apd', 'fid', 'gmd', 'timeDelayStage', 'timeNeg', 'timePos']
myDataSetNames = list(f)

enumeratedApd = enumerate(f[list(f)[0]])
enumeratedFid = enumerate(f[list(f)[1]])
enumeratedGmd = enumerate(f[list(f)[2]])
enumeratedTimeDelayStage = enumerate(f[list(f)[3]])
enumeratedTimeToolNegative = enumerate(f[list(f)[4]])
enumeratedTimeToolPositive = enumerate(f[list(f)[5]])

myApdList=array([])
myFidList=array([])
myGmdList=array([])
myTimeDelayList = array([])
myTimeToolNegativeList = array([])
myTimeToolPositiveList = array([])


myNormalizedApdList = array([])

myHistogramNegativeTimeTotal = 0
myHistogramPositiveTimeTotal = 0

timeStep = 0.0125
xEdges = arange(40.0,54.006,timeStep)	#timing
yEdges = arange(0,0.08,.00001)	#intensity apd/gmd

timingRange = array([])

myDict= {}
for i in xEdges:
	myDict[str(timeStep*round(i/timeStep))] = array([0,0])

myApdGmdDict = {}
myApdGmdDictCounter = {}
for i in arange(-3e9,10e10,1e8):
	myApdGmdDict[str(i)] = 0 
	myApdGmdDictCounter[str(i)] = 0
myApdGmdDict['-0.0'] = 0 
myApdGmdDictCounter['-0.0'] = 0

for i in arange(0,361777,1):
	
	try:
		thisApdEvent,thisApdValue = next(enumeratedApd)
		thisFidEvent,thisFidValue = next(enumeratedFid)
		thisGmdEvent,thisGmdValue = next(enumeratedGmd)
	
		thisTimeDelayEvent,thisTimeDelayValue = next(enumeratedTimeDelayStage)
		thisTimeToolNegativeEvent,thisTimeToolNegativeValue = next(enumeratedTimeToolNegative)
		thisTimeToolPositiveEvent,thisTimeToolPositiveValue = next(enumeratedTimeToolPositive)
	
		#if any in [thisApdEvent,thisApdValue,thisFidEvent,thisFidValue,thisGmdEvent,thisGmdValue]==None
		tempIndex = str(1e8*round(thisGmdValue/1e8))
		try:

			if any([None is k for k in [thisApdEvent,thisApdValue,thisFidEvent,thisFidValue,thisGmdEvent,thisGmdValue,myApdGmdDict[tempIndex],myApdGmdDictCounter[tempIndex]]]):
				print("evt {} is no good".format(i))
				continue
		except KeyError:
			print("evt {} is no good".format(i))
			continue
		

		#min and max of time delay stage list are 51.686 and 52.0001. based on previous turnerAnalysis.py, the units must be nanoseconds
		#myApdList*1.0/myGmdList ranges from 0 to 0.008

		if (i%1000 == 999):
			if(sum(myGmdList!=0)):
				print("event number {}".format(thisApdEvent))
				myHistogram = np.histogram2d(myTimeDelayList+0*(myTimeToolPositiveList-336.5),(myApdList*1.0/myGmdList), bins=(xEdges, yEdges))[0]
				myHistogramPositiveTimeTotal = myHistogramPositiveTimeTotal + myHistogram

				myHistogram = np.histogram2d(myTimeDelayList+0*(myTimeToolNegativeList-336.5),(myApdList*1.0/myGmdList), bins=(xEdges, yEdges))[0]
				myHistogramNegativeTimeTotal = myHistogramNegativeTimeTotal + myHistogram
				#H, xedges, yedges = np.histogram2d(y, x, bins=(xedges, yedges))
				#myHistogram, xedges, yedges = np.histogram2d(myTimeDelayList,(myApdList/myGmdList), bins=(xedges, yedges))

				timingRange = append(timingRange,mean(myTimeDelayList))

			myApdList=array([])
			myFidList=array([])
			myGmdList=array([])
			myTimeDelayList = array([])
			myNormalizedApdList = array([])
			myTimeToolNegativeList = array([])
			myTimeToolPositiveList = array([])			


		
		myApdGmdDict[tempIndex] += thisApdValue
		myApdGmdDictCounter[tempIndex] += 1

		#if(thisGmdValue<5e10 and thisGmdValue>1.2e10):
		#if(thisGmdValue>1.2e9 and thisGmdValue<1.2e10):
		if(thisGmdValue>1.1e9 and thisGmdValue<5e10):
			#xEdges = arange(49.0,52,0.015)	#timing
			
			tempIndex = str(timeStep*round(thisTimeDelayValue/timeStep))
			
			#pickle.dump(myDict, open( "dictifiedData.pkl", "wb" ) ) #how to write and read the dictionary to pickle
			#temp = pickle.load(open("dictifiedData.pkl","rb"))

			myDict[tempIndex] = vstack([myDict[tempIndex],array([thisGmdValue,thisApdValue]) ])

			myApdList = append(myApdList,thisApdValue)
			myFidList = append(myFidList,thisFidValue)
			myGmdList = append(myGmdList,thisGmdValue)
			myTimeDelayList = append(myTimeDelayList,thisTimeDelayValue)
			myTimeToolNegativeList = append(myTimeToolNegativeList,thisTimeToolNegativeValue)
			myTimeToolPositiveList = append(myTimeToolPositiveList,thisTimeToolPositiveValue)


	except KeyboardInterrupt:
		break

print("event number {}".format(thisApdEvent))
myHistogram = np.histogram2d(myTimeDelayList+myTimeToolPositiveList*1.0/1000,(myApdList*1.0/myGmdList), bins=(xEdges, yEdges))[0]
myHistogramPositiveTimeTotal = myHistogramPositiveTimeTotal + myHistogram

myHistogram = np.histogram2d(myTimeDelayList+myTimeToolNegativeList*1.0/1000,(myApdList*1.0/myGmdList), bins=(xEdges, yEdges))[0]
myHistogramNegativeTimeTotal = myHistogramNegativeTimeTotal + myHistogram
#H, xedges, yedges = np.histogram2d(y, x, bins=(xedges, yedges))
#myHistogram, xedges, yedges = np.histogram2d(myTimeDelayList,(myApdList/myGmdList), bins=(xedges, yedges))

pickle.dump(myDict, open( "dictifiedDataRun"+str(runNumber)+".pkl", "wb" ) ) #how to write and read the dictionary to pickle
