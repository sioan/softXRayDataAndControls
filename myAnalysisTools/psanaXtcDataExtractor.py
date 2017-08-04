#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
import argparse
import os
import sys
sys.path.append(os.curdir) 
from config import analysisFunctions
from pylab import *
import psana
import subprocess
import time
import h5py

#this small data wrapper is to swap out small data implementations 
#depending whether MPIDataSouce or plain data source is used

class SmallData():
	def __init__(self,h5FileName):
		self.h5FileObject = h5py.File(h5FileName, 'w')
		self.eventNumber = 1
		
	def event(self,dataDictionary):
		if(self.eventNumber != 1 ):
			for i in dataDictionary:
				self.h5FileObject[i].resize((self.eventNumber+1,))
				self.h5FileObject[i][self.eventNumber] = dataDictionary[i]
				#print("succeded")
				

		else:
			for i in dataDictionary:
				#print("failed")
				#print(dataDictionary[i])
				self.h5FileObject.create_dataset(i,(0,),dtype='f8',maxshape=(None,))
				self.h5FileObject[i].resize((self.eventNumber,))
				self.h5FileObject[i][0] = dataDictionary[i]

		self.eventNumber = self.eventNumber + 1
		
	def save(self,summaryDictionaryData):
		for i in summaryDictionaryData:
			self.h5FileObject[i] = summaryDictionaryData[i]

	def close(self):
		self.h5FileObject.close()

def makeDataSourceAndSmallData(experimentNameAndRun,h5FileName,MPI):

	if(MPI==False):
		print("loading experiment data using MPI ")
		myDataSource = psana.MPIDataSource(experimentNameAndRun+":smd")	#this needs to be merged

		print("defining small data")
		smldata = myDataSource.small_data(h5FileName)
	else:
		print("loading experiment data NOT using MPI ")
		myDataSource = psana.MPIDataSource(experimentNameAndRun)	#this is hook for non mpi

		print("defining small data. hook in place ")
		smldata = SmallData(h5FileName)


	return (myDataSource,smldata)

def generateDetectorDictionary(configFileName):

	myWorkingDirectory = subprocess.check_output("pwd")[:-1]
	print("working directory = "+str(myWorkingDirectory))

	print("reading config file")
	f = open(myWorkingDirectory+"/config/"+configFileName,'r')
	myDetectorObjectDictionary = {}
	myDetectorObjectDictionary['analyzer'] = {}
	myDetectorObjectDictionary['summarizer'] = {}				
	print("Generating analyzer summarizer and detector objects")
	#print(str(analysisFunctions.__dict__.keys()))	

	for thisDetectorConfig in f:
		if('#'  not in thisDetectorConfig):
			myParsedString = thisDetectorConfig.split(',')
			print(thisDetectorConfig)
			print("found detector object named "+myParsedString[3])
			myDetectorObjectDictionary[myParsedString[3]] = psana.Detector(myParsedString[0])
			myDetectorObjectDictionary['analyzer'][myParsedString[3]] = analysisFunctions.__dict__[myParsedString[4]]
			if(myParsedString[5]!='None'):		
				myDetectorObjectDictionary['summarizer'][myParsedString[3]] = analysisFunctions.__dict__[myParsedString[5]]

		else:
			continue
		
	return myDetectorObjectDictionary

def initializeDataDictionaries(myDetectorObjectDictionary):

	myDataDictionary = {}
	summaryDataDictionary={}
	for i in myDetectorObjectDictionary['summarizer']:
		summaryDataDictionary[i] = 0

	return[myDataDictionary,summaryDataDictionary]
def renameSummaryKeys(myDict):
	for i in myDict:
		myDict[i+'Summarized'] = myDict.pop(i)

def main(exp, run, configFileName,h5FileName,testSample,MPI):
	global smldata,	summaryDataDictionary,myDataDictionary,myEnumeratedEvents

	startTime = time.time()
	print("entering main function")
	
	h5FileName = exp+'run'+str(run)+'.h5'
	
	try:
		print("removing file")
		os.system("rm "+h5FileName)
	except:
		print("nothing to remove")
	
	experimentNameAndRun = "exp=%s:run=%d"%(exp, run)
	#print("loading experiment")
	#myDataSource = psana.MPIDataSource(experimentNameAndRun+":smd")	#this needs to be merged

	#print("defining small data")
	#smldata = myDataSource.small_data(h5FileName)

	myDataSource, smldata = makeDataSourceAndSmallData(experimentNameAndRun,h5FileName,MPI)

	print("loading detector object dictionary")
	myDetectorObjectDictionary = generateDetectorDictionary(configFileName)
	print("detector object dictionary loaded")
	
	print("initializing data dictionaries")
	myDataDictionary,summaryDataDictionary = initializeDataDictionaries(myDetectorObjectDictionary)

	messageFeedBackRate = 20+980*int(testSample==False)
	
	print("iterating over enumerated events")
	
	myEnumeratedEvents = enumerate(myDataSource.events())
	for eventNumber,thisEvent in myEnumeratedEvents:
		if(eventNumber %messageFeedBackRate == 1):
			print("iterating over enumerated events.  Event number = "+str(eventNumber)+" Elapsed Time (s) = "+str(time.time()-startTime))
		if(testSample):
			if(eventNumber > 200):
				break
		
		for i in myDetectorObjectDictionary['analyzer']:
			myDataDictionary[i] = myDetectorObjectDictionary['analyzer'][i](myDetectorObjectDictionary[i],thisEvent)
		for i in myDetectorObjectDictionary['summarizer']:
				summaryDataDictionary[i] = myDetectorObjectDictionary['summarizer'][i](myDetectorObjectDictionary[i],thisEvent,summaryDataDictionary[i])

		smldata.event(myDataDictionary)
		
	

	print("finished looping over events")
	print("saving small data")
	#print(summaryDataDictionary)
	renameSummaryKeys(summaryDataDictionary)
	smldata.save(summaryDataDictionary)
	#smldata.save()
	print("small data file saved")
	#smldata.close()
	print("small data file closed")

	return

if __name__ == '__main__':
	
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	myParser.add_argument('-e','--exp', help='the experiment name')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-c','--configFile',help='the config file to write to')
	myParser.add_argument('-hd5','--hd5File',help='the small data file to write to')
	myParser.add_argument('-t','--testSample',action='store_true',help='only take a small set of data for testing')
	myParser.add_argument('-m','--MPI',action='store_true',help='does not use mpi ')

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(
		myArguments.exp,
		myArguments.run,
		myArguments.configFile,
		myArguments.hd5File,
		myArguments.testSample,
		myArguments.MPI)
