#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python

#--------------------------------------------------------------------------
# File and Version Information:
#  $Id: README 2017-08-06 18:54:12Z sioan@SLAC.STANFORD.EDU $
#
# Description:
#  README file for data analysis
#------------------------------------------------------------------------

#Package author: Sioan Zohar

#Brief description:
#==================
#Abstracts away details of psana, small data, and allows users to focus on developing scientific analysis code.
#
#==================

#to run interactively 
#ipython -i ../../myAnalysisTools/psanaXtcDataExtractor.py -- -e sxri0414 -r 79 -td TSS_OPAL -tc 162 -f 150 -s 4 -t

#to run on batch nodes
#bsub -o %J.log -q psnehprioq -n 48 mpirun --mca btl ^openib psanaXtcDataExtractor.py -e sxri0414 -r 60 -td TSS_OPAL -tc 162

#mpi for specified hosts
#mpirun -n 40 --host daq-amo-mon02,daq-amo-mon03,daq-amo-mon04,daq-amo-mon05,daq-amo-mon06 amon0816.sh

#==================


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
import TimeTool

#this small data wrapper is to swap out small data implementations 
#depending whether MPIDataSouce or plain data source is used
ttAnalyze = None

def makeDataSourceAndSmallData(experimentNameAndRun,h5FileName,ttDevice,ttCode):
	global ttAnalyze
	smldata = "None"
	if(ttDevice is not None ):

		print("setting up time tool.") 
		print("Device = "+ttDevice)
		print("bykick code = "+str(ttCode)) 
		ttOptions = TimeTool.AnalyzeOptions(get_key=ttDevice,eventcode_nobeam = ttCode)
		ttAnalyze = TimeTool.PyAnalyze(ttOptions)
	
		print("loading experiment data using standard small data")
		myDataSource = psana.MPIDataSource(experimentNameAndRun,module=ttAnalyze)	

		print("defining small data")
		if(h5FileName!="None"):
			smldata = myDataSource.small_data(h5FileName)
	else:
		print("loading experiment using custom small data")
		myDataSource = psana.MPIDataSource(experimentNameAndRun)

		print("defining small data. hook in place ")
		if(h5FileName!="None"):
			smldata = myDataSource.small_data(h5FileName)


	return (myDataSource,smldata)

def generateDetectorDictionary(configFileName):
	global ttAnalyze

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

		if(ttAnalyze is not None):
			print("casting time tool as detector object")
			myDetectorObjectDictionary['TSS_OPAL'] = ttAnalyze
			myDetectorObjectDictionary['analyzer']['TSS_OPAL'] = analysisFunctions.__dict__['getTimeToolData']
			#myDetectorObjectDictionary['summarizer']['TSS_OPAL'] = None
		
	return myDetectorObjectDictionary

def initializeDataDictionaries(myDetectorObjectDictionary):

	myDataDictionary = {}
	summaryDataDictionary={}
	for i in myDetectorObjectDictionary['summarizer']:
		summaryDataDictionary[i] = 0

	return[myDataDictionary,summaryDataDictionary]
def renameSummaryKeys(myDict):
	tempKeys = myDict.keys()
	for i in tempKeys:
		myDict[i+'Summarized'] = myDict.pop(i)

def main(myExp, myRun, configFileName,h5FileName,testSample,ttDevice,ttCode,startEvent,finalEvent):
	global smldata,	summaryDataDictionary,myDataDictionary,myEnumeratedEvents,eventNumber,thisEvent,myDetectorObjectDictionary
	#global myExp,myRun
	print ("exp = "+str(myExp))
	print ("run = "+str(myRun))
	startTime = time.time()
	print("entering main function")
	
	experimentNameAndRun = "exp=%s:run=%d:smd"%(myExp, myRun)
	#print("loading experiment")
	#myDataSource = psana.MPIDataSource(experimentNameAndRun+":smd")	#this needs to be merged

	#print("defining small data")
	#smldata = myDataSource.small_data(h5FileName)
	
	if(h5FileName!="None"):
		h5FileName = myExp+'run'+str(myRun)+str(h5FileName)+'.h5'
		print("removing file")
		os.system("rm "+h5FileName)
	
	myDataSource, smldata = makeDataSourceAndSmallData(experimentNameAndRun,h5FileName,ttDevice,ttCode)

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
			
		if(eventNumber<startEvent):
			continue
		if(testSample or (finalEvent > 0)):
			if(eventNumber > finalEvent):
				break
		
		for i in myDetectorObjectDictionary['analyzer']:
			myDataDictionary[i] = myDetectorObjectDictionary['analyzer'][i](myDetectorObjectDictionary[i],thisEvent)
	

		for i in myDetectorObjectDictionary['summarizer']:
				summaryDataDictionary[i] = myDetectorObjectDictionary['summarizer'][i](myDetectorObjectDictionary[i],thisEvent,summaryDataDictionary[i])

		#for i in myDataDictionary:
		if any([None is myDataDictionary[k] for k in myDataDictionary]):
			continue
		#	if (None is myDataDictionary[i]):
		#		del myDataDictionary[i]

		if(h5FileName!="None"):
			smldata.event(myDataDictionary)


	print("finished looping over events")
	if(h5FileName!="None"):
		print("saving small data")
	
		renameSummaryKeys(summaryDataDictionary)
		smldata.save(summaryDataDictionary)
		print("small data file saved")
		#smldata.close()
		print("small data file closed")

	return

if __name__ == '__main__':
	
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	myParser.add_argument('-e','--exp', help='the experiment name')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-c','--configFile',help='the config file to read from',default='analysis.cfg')
	myParser.add_argument('-hd5','--hd5File',help='extension of the small data file to write to. typically a,b or c',default="")
	myParser.add_argument('-t','--testSample',action='store_true',help='only take a small set of data for testing')
	myParser.add_argument('-td','--ttDevice',type=str,help='device to use for getting time tool ', default=None)
	myParser.add_argument('-tc','--ttCode',type=int,help='event code to identify by kick', default=None)
	
	myParser.add_argument('-s','--start',type=int,help='skips until starting event reached', default=-1)
	myParser.add_argument('-f','--final',type=int,help='up to final event', default=1e12)
	

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(
		myArguments.exp,
		myArguments.run,
		myArguments.configFile,
		myArguments.hd5File,
		myArguments.testSample,
		myArguments.ttDevice,
		myArguments.ttCode,
		myArguments.start,
		myArguments.final)
