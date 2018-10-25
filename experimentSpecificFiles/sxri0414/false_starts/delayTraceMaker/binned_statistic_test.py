#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/ipython -i
import pickle
import time
from pylab import *
from lib.analysis_library import apply_filter
from lib.analysis_library import median_sorted_filter
import h5py
import os
import sys
import IPython
from hdf5_to_dict import hdf5_to_dict
from filterMasks import filterMasks
from scipy.optimize import curve_fit
from plotPackage import errorWeightedSmoothing
from scipy.interpolate import interp1d
#fit's data to log
from scipy.stats import binned_statistic_dd

def t_func(r):
	temp = array([pickle.loads(i) for i in r])
	
	x=temp[:,0]
	y=temp[:,1]
	#if len(x)<len(y): y=y[:-1]
	#elif len(x)>len(y): x=x[:-1]
	#elif (len(x)==0): return nan

	#IPython.embed()

	myLength=len(y)
	threshold=0.05
	ySortedIndex = argsort(y)
	y = y[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	x = x[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	
	xSortedIndex = argsort(x)
	y = y[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	x = x[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]

	#print(str(len(x))+", "+str(len(y))+", "+str(len(r)))
	#print(str(len(x))+", "+str(len(y)))
	
	myCov = cov(x,y)
	mySlope = myCov[0,1]/myCov[0,0]

	return mean(y)/mean(1.0*x)
	#return mySlope

def s_func(r):
	temp = array([pickle.loads(i) for i in r])
	print(temp.shape)
	return 1


if __name__ == '__main__':

	#load data
	TOP="/reg/neh/home5/sioan/Desktop/softXRayDataAndControls/experimentSpecificFiles/sxri0414/"
	experimentRunName = "sxri0414run60"
	myFile = experimentRunName+".h5"
	myHdf5Object = h5py.File(TOP+"smallHdf5Data/"+myFile,"r")
	myDataDict = hdf5_to_dict(myHdf5Object)

	#createFilter filter
	myMask =  filterMasks.__dict__[experimentRunName](myHdf5Object)


	#make I vs I0 calibration
	dd = apply_filter(myDataDict,myMask)
	binned_axes = array([dd['atm_corrected_timing'],dd['ebeam/photon_energy']]).transpose()
	#arg_axes = array([str(i) for i in array([dd['acqiris2'],dd['GMD']]).transpose()])
	arg_axes = array([pickle.dumps(i) for i in array([dd['GMD'],dd['acqiris2']]).transpose()])	#17 seconds on run 60.
	tEdges = arange(327,346.5,0.075)
	#eEdges = arange(900,930,0.25)
	#eEdges = append(append(900,arange(912.5,916.5,.5)),920)
	eEdges = array([900,912.5,914.5,916.5,920])
	

	#temp = binned_statistic_dd(sample=binned_axes,values=ones(len(arg_axes[0])),bins=(tEdges,eEdges), statistic=t_func)
	covxy = binned_statistic_dd(binned_axes,arg_axes,bins=(tEdges,eEdges),statistic=t_func) 

	#myRange = [str(i)+"test" for i in arange(len(dd['GMD']))]
	#testing if passes string. it works. also works on pickled array
	#covxy = binned_statistic_dd(binned_axes,arg_axes,bins=(tEdges,eEdges),statistic=s_func) 
	#covxy = binned_statistic_dd(binned_axes,dd['acqiris2']*dd['GMD'],bins=(tEdges,eEdges))	#this works. not really
	#varxx = binned_statistic_dd(binned_axes,dd['GMD']*dd['GMD'],bins=(tEdges,eEdges))		#this works. not really

	u,s,v = svd(covxy[0])

	subplot(111)
	#plot(-1*tEdges[:-1],sum(covxy[0],axis=1))
	plot(-1*tEdges[:-1],covxy[0][:,0])
	plot(-1*tEdges[:-1],covxy[0][:,1])
	plot(-1*tEdges[:-1],covxy[0][:,2])
	plot(-1*tEdges[:-1],covxy[0][:,3])



	show()

