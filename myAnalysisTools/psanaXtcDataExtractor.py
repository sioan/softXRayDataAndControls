import argparse
import analysisFunctions
from pylab import *
import psana
import os

def generateDetectorDictionary(configFileName):
	
	f = open(configFileName+'.cfg','r')
	myDetectorObjectDictionary = {}
	myDetectorObjectDictionary['analyzer'] = {}
	
	for thisDetectorConfig in f:
		if('#'  not in thisDetectorConfig):
			myParsedString = thisDetectorConfig.split(',')
			myDetectorObjectDictionary[myParsedString[3]] = psana.Detector(myParsedString[0])
			myDetectorObjectDictionary['analyzer'][myParsedString[3]] = analysisFunctions.__dict__[myParsedString[4]]
		else:
			continue
		
	return myDetectorObjectDictionary


def main(exp, run, configFileName,h5FileName):
	try:
		os.system("rm "+h5FileName+".h5")
	except:
		print("nothing to remove")
	
	experimentNameAndRun = "exp=%s:run=%d"%(exp, run)
	myDataSource = psana.MPIDataSource(experimentNameAndRun)
	smldata = myDataSource.small_data(h5FileName+'.h5')

	myDetectorObjectDictionary = generateDetectorDictionary(configFileName)
	
	myDataDictionary = {}

	myEnumeratedEvents = enumerate(myDataSource.events())
	for eventNumber,thisEvent in myEnumeratedEvents:
		if(eventNumber > 10):
			break
		
		for i in myDetectorObjectDictionary.keys():
			if (i!='analyzer'):
				myDataDictionary[i] = myDetectorObjectDictionary['analyzer'][i](myDetectorObjectDictionary[i],thisEvent)
		
		smldata.event(myDataDictionary)
		
	#summary = myDetectorObjectDictionary['names'].copy()
	#summary.update(myEpicsDetectorObjectDictionary['epics']['names'])
	#smldata.save(summary)
	smldata.save()
	smldata.close()

	return

if __name__ == '__main__':
	myParser = argparse.ArgumentParser(description='Generating a config file for analysis')
		
	myParser.add_argument('-e','--exp', help='the experiment name')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-c','--configFile',help='the config file to write to')
	myParser.add_argument('-hd5','--hd5File',help='the small data file to write to')

	myArguments = myParser.parse_args()

	main(myArguments.exp,myArguments.run,myArguments.configFile,myArguments.hd5File)
