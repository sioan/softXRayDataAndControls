from pylab import *
import h5py
f = h5py.File("run60.h5")

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

xEdges = arange(49.0,52,0.015)	#timing
yEdges = arange(0,0.08,.00001)	#intensity

timingRange = array([])

for i in arange(0,261777,1):
	
	try:
		thisApdEvent,thisApdValue = next(enumeratedApd)
		thisFidEvent,thisFidValue = next(enumeratedFid)
		thisGmdEvent,thisGmdValue = next(enumeratedGmd)
	
		thisTimeDelayEvent,thisTimeDelayValue = next(enumeratedTimeDelayStage)
		thisTimeToolNegativeEvent,thisTimeToolNegativeValue = next(enumeratedTimeToolNegative)
		thisTimeToolPositiveEvent,thisTimeToolPositiveValue = next(enumeratedTimeToolPositive)
	
		#if any in [thisApdEvent,thisApdValue,thisFidEvent,thisFidValue,thisGmdEvent,thisGmdValue]==None
		if any([None is k for k in [thisApdEvent,thisApdValue,thisFidEvent,thisFidValue,thisGmdEvent,thisGmdValue]]):
			print("evt {} is no good".format(i))

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


		if(thisGmdValue>1.7e10):
			myApdList = append(myApdList,thisApdValue)
			myFidList = append(myFidList,thisFidValue)
			myGmdList = append(myGmdList,thisGmdValue)
			myTimeDelayList = append(myTimeDelayList,thisTimeDelayValue)
			myTimeToolNegativeList = append(myTimeToolNegativeList,thisTimeToolNegativeValue)
			myTimeToolPositiveList = append(myTimeToolPositiveList,thisTimeToolPositiveValue)


	except:
		break

print("event number {}".format(thisApdEvent))
myHistogram = np.histogram2d(myTimeDelayList+myTimeToolPositiveList*1.0/1000,(myApdList*1.0/myGmdList), bins=(xEdges, yEdges))[0]
myHistogramPositiveTimeTotal = myHistogramPositiveTimeTotal + myHistogram

myHistogram = np.histogram2d(myTimeDelayList+myTimeToolNegativeList*1.0/1000,(myApdList*1.0/myGmdList), bins=(xEdges, yEdges))[0]
myHistogramNegativeTimeTotal = myHistogramNegativeTimeTotal + myHistogram
#H, xedges, yedges = np.histogram2d(y, x, bins=(xedges, yedges))
#myHistogram, xedges, yedges = np.histogram2d(myTimeDelayList,(myApdList/myGmdList), bins=(xedges, yedges))
