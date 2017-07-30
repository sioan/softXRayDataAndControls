from pylab import *
import psana
import os

os.system("rm mySmallData.h5")

#myDataSource = psana.DataSource("shmem=psana.0:stop=no")
myDataSource = psana.MPIDataSource("exp=sxri0414:run=79")
smldata = myDataSource.small_data('mySmallData.h5')

#myDataAnalysisDictionary = {}
#	myDataAnalysis

myDetectorObjectDictionary = {}
for i in psana.DetNames():
	#print i[0]
	if('image' in dir(psana.Detector(i[0]))):
		#print i[0]
		myDetectorObjectDictionary[i[0]] = psana.Detector(i[0]).image

	else: 
		myDetectorObjectDictionary[i[0]] = psana.Detector(i[0])

myEpicsDetectorObjectDictionary = {}
for i in psana.DetNames('epics'):
	myEpicsDetectorObjectDictionary['epics',i[0]] = psana.Detector(i[0])

myEnumeratedEvents = enumerate(myDataSource.events())
myDataDictionary = {}

#for eventNumber,thisEvent in myEnumeratedEvents:
while (True):

	eventNumber,thisEvent  = next(myEnumeratedEvents)
	print eventNumber
	if(eventNumber > 200):
		break
	#for i in myDetectorObjectDictionary.keys():
		#print i
	#	try:
	#		myDataDictionary[i] = myDetectorObjectDictionary[i](thisEvent)
	#	except:
	#		continue
	
	for i in myEpicsDetectorObjectDictionary.keys():
		try:
				myDataDictionary[i[0]][i[1]] = myEpicsDetectorObjectDictionary[i](thisEvent)
		except:
				myDataDictionary[i[0]] = {}

	#smldata.event(myDataDictionary)
	smldata.event(test=eventNumber)

summary = {}
summary['test'] = 0

#smldata.save(summary)
smldata.save()
#smldata.close()
