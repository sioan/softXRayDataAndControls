from pylab import *
from scipy.interpolate import interp1d
import h5py


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
#takes an hdf5 files turns it into applies a mask, turns it into dictionary, and bins it according to a config file or parameters
#the idea is to iterate this same code on different data sets using one config file or to test out analysis approaches by evaluating one data set and
#many config files iterating over different config files.  Testing different analysis techniques (that are abstracted into different configurations of identical code)
#is important for understanding why somes analysis techniques gives the expected result and some give unexpceted results.

#In depth description
#====================

#this is being abstracted from previous attempts to analyze SXRI0414.  how to abstract the approaches taken so far. they are
#1) the brute force standard deviation and mean.  (original provided by h5 file by pi.  gives the slow oscillation without much effort.)
#2) the elegant filtering using glue to get rid of zeros.
#3) and projection onto calibration curve gave nice slow oscillations.
#4) parsing the different scans.  didn't give oscillations. nice scans. fiducials odd vs even do correspond to event code 141

#4) binning acqiris/gmd for different delay stages (this is important. close to brute force)/. result is 2d. gona fit this data. want to understand maths of 
#fitting binned data.  This wasn't brute, but projection onto acqiris vs gmd calibration using calibration i0 as errorless x. not correct. but total least squares has fudge factor for weighting different detectors.
#5) making stage of acqiris vs gmd images for different delays. result is 3d data set.  too sparse in this case... yes?.  Used image j dynamic z_profiler to get delay axis. not intended result since each pixel is a count, not a normalized acqiris/gmd

#6) filtered on odd/even fiducials. should be the same event code as 141.  (the time tool bimodal distribution becomes a single mode when filtering on).  

#combo of brute force and fiducial filtering get's the oscillations.  parsing the different scans doesn't yield the oscillations.

#how to 3d and 2d data sets, abstracting is almost intuitive, but still needs some thought.  parsing each delay stage scan. the result is.... that's binned... into big time buckets. roughly equal length. so it's a 3d data set? yes. acqiris/gmd, delay stage, and big time buckets that correspond to human experienced time needed to finish one of the scans.  that becomes a 3d cube. if broken up into acqiris, gmd, delay stage, and scan #, that becomes a 4d cube.
  

#histogramdd. that should bin is as desired.  but how to get it into a format other programs like glue or imagej can use?  how to to make it so imagej's dynamic profiler can work on it without discounting weighting from 

#which way to plot? Which way to sum? Which slice or projection?  along which axis?

#turner normalize on event by event. silke normalizes averaged over several events.
#tim subtracts laser off shots
#filter on bad time tool amplitudes.

#notes from josh for sxri. doesn't belong here, needs to find a home.
#x-value (time in ps) = x-value (position of stage in mm) * 2 / c0
#where c0 should be 0.299792458 (speed of light in mm/ps)

#==================
#final product




#==================

def hdf5_to_dict(myhdf5Object):
	replacementDictionary = {}
	for i in myhdf5Object:
		print(str(myhdf5Object[i]))
		if ('dataset' in str(myhdf5Object[i])):
			print("dataset is in"+str(myhdf5Object[i]))
			if ('Summarized' not in str(myhdf5Object[i])):
				replacementDictionary[i] = nan_to_num(myhdf5Object[i])
			else:
				x=1	
		else:
			replacementDictionary[i] = {}
			print("dataset is not in"+str(myhdf5Object[i]))
			print(i)
			replacementDictionary[i] = hdf5_to_dict(myhdf5Object[i])

	return replacementDictionary

def main():

if __name__ == '__main__':
	
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	myParser.add_argument('-f','--file name', help='file name')
	myParser.add_argument('-d','--run',type=int,help='dictionary keys identifying data to bin',default=None)
	myParser.add_argument('-c','--configuration file if the flags here are not helpful ',help='the config file to read from')
	myParser.add_argument('-hd5','--hd5File',help='extension of the small data file to write to. typically a,b or c',default="")
	myParser.add_argument('-t','--testSample',action='store_true',help='only take a small set of data for testing')
	myParser.add_argument('-m','--MPI',action='store_true',help='does not use mpi ')
	myParser.add_argument('-s','--start',type=int,help='skips until starting event reached', default=-1)

	myArguments = myParser.parse_args()
	print("arguments parsed")

	main(
		myArguments.exp,
		myArguments.run,
		myArguments.configFile,
		myArguments.hd5File,
		myArguments.testSample,
		myArguments.MPI,
		myArguments.start)
