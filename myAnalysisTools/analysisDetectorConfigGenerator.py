#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
#from pylab import *
import sys
import os
sys.path.append(os.curdir) 
import argparse
import psana



def main(exp, run, configFileName):

	experimentNameAndRun = "exp=%s:run=%d"%(exp, run)
	try:
		os.system('mkdir config')
	except:
		print("won't throw an exceptoin even if it exists")

	os.system('./config/touch __init__.py')

	myDataSource = psana.MPIDataSource(experimentNameAndRun)
	f = open('./config/'+configFileName+'.cfg','w')

	f.write('##########################\n')
	f.write('#######DAQ DEVICES########\n')
	f.write('##########################\n')

	for thisDetectorName in psana.DetNames():
		#f.write('#detectorStart, ')
		f.write('#')
		for i in thisDetectorName:
			f.write(str(i)+', ')
		#f.write(' detectorFinish')
		f.write('\n')
	f.write('##########################\n')
	f.write('#######EPICS PVs##########\n')
	f.write('##########################\n')

	for thisDetectorName in psana.DetNames('epics'):
		f.write('#')
		for i in thisDetectorName:
			f.write(str(i)+', ')
		#f.write(' epicsPvFinish')
		f.write('\n')
	f.close()

	

if __name__ == '__main__':
	myParser = argparse.ArgumentParser(description='Generating a config file for analysis')
	#myGroup = myParser.add_mutually_exclusive_group()
	
	myParser.add_argument('-e','--exp', help='the experiment name')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-c','--configFile',help='the config file to write to')

	myArguments = myParser.parse_args()

	main(myArguments.exp,myArguments.run,myArguments.configFile)
