#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
import argparse
import analysisFunctions
from pylab import *
import psana
import os

def generateDetectorDictionary(configFileName):
	print("reading config file")
	f = open(configFileName+'.cfg','r')
	myDetectorObjectDictionary = {}
	myDetectorObjectDictionary['analyzer'] = {}
	
	for thisDetectorConfig in f:
		if('#'  not in thisDetectorConfig):
			myParsedString = thisDetectorConfig.split(',')
			print("found detector object named "+myParsedString[3])
			myDetectorObjectDictionary[myParsedString[3]] = psana.Detector(myParsedString[0])
			myDetectorObjectDictionary['analyzer'][myParsedString[3]] = analysisFunctions.__dict__[myParsedString[4]]
		else:
			continue
		
	return myDetectorObjectDictionary


def main(exp, run, configFileName,h5FileName):
	print("entering main function")

	try:
		print("removing file")
		os.system("rm "+h5FileName+".h5")
	except:
		print("nothing to remove")
	
	print("loading experiment")
	experimentNameAndRun = "exp=%s:run=%d"%(exp, run)
	myDataSource = psana.MPIDataSource(experimentNameAndRun+":smd")

	print("defining small data")
	smldata = myDataSource.small_data(h5FileName+'.h5')

	print("loading detector object dictionary")
	myDetectorObjectDictionary = generateDetectorDictionary(configFileName)
	print("detector object dictionary loaded")
	
	myDataDictionary = {}
	print("iterating over enumerated events")
	myEnumeratedEvents = enumerate(myDataSource.events())
	for eventNumber,thisEvent in myEnumeratedEvents:
		if(eventNumber %1000 == 1):
			print("iterating over enumerated events.  Event number = "+str(eventNumber))
		
		#if(eventNumber > 200):
			#break
		
		for i in myDetectorObjectDictionary.keys():
			if (i!='analyzer'):
				myDataDictionary[i] = myDetectorObjectDictionary['analyzer'][i](myDetectorObjectDictionary[i],thisEvent)
		
		smldata.event(myDataDictionary)
		
	#summary = myDetectorObjectDictionary['names'].copy()
	#summary.update(myEpicsDetectorObjectDictionary['epics']['names'])
	#smldata.save(summary)

	print("finished looping over events")
	print("saving small data")
	smldata.save()
	print("small data file saved")
	smldata.close()
	print("small data file closed")

	return

if __name__ == '__main__':
	
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Generating a config file for analysis')
		
	myParser.add_argument('-e','--exp', help='the experiment name')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-c','--configFile',help='the config file to write to')
	myParser.add_argument('-hd5','--hd5File',help='the small data file to write to')

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(myArguments.exp,myArguments.run,myArguments.configFile,myArguments.hd5File)