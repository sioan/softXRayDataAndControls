#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.58/bin/python
import argparse
from pylab import *
import psana
import IPython

def main(argd):

	if(False==argd['shared_mem']):
		experimentNameAndRun = "exp=%s:run=%d:smd"%(argd['exp'], argd['run'])
		myDataSource = psana.MPIDataSource(experimentNameAndRun+":smd")
	else:
		experimentNameAndRun ="shmem=psana.0:stop=no"
		myDataSource = psana.DataSource(experimentNameAndRun)
	myEnumeratedEvents = enumerate(myDataSource.events())
	
	smldata = myDataSource.small_data("test.h5")

	for eventNumber, thisEvent in myEnumeratedEvents:
		if eventNumber<argd['start']:continue
		if eventNumber>argd['final']: break

		if(eventNumber%200==1):
			print eventNumber

		smldata.event()

	smldata.save()

	IPython.embed()

if __name__ == '__main__':
	
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
	myParser.add_argument('-e','--exp', help='the experiment name')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-s','--start',type=int,help='skips until starting event reached', default=-1)
	myParser.add_argument('-f','--final',type=int,help='up to final event. default is 100', default=100)
	myParser.add_argument('-sh','--shared_mem',action='store_true',help='shared memory',default=False)
	

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(myArguments.__dict__)
