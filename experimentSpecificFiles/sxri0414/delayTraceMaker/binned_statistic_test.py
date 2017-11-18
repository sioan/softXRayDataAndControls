#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/ipython -i
from pylab import *
from lib.analysis_library import apply_filter
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
arg_axes = array([dd['acqiris2'],dd['GMD']])
tEdges = arange(325,348,0.1)
#eEdges = arange(900,930,0.25)
eEdges = append(append(900,arange(912.5,916.5,.5),920)

def t_func(r):
	#r=array([[-1,1],[2,-3]])
	x=r[::2]
	y=r[1::2]
	if len(x)<len(y): y=y[:-1]
	elif len(x)>len(y): x=x[:-1]
	elif (len(x)==0): return -99

	#print(str(len(x))+", "+str(len(y))+", "+str(len(r)))
	#print(str(len(x))+", "+str(len(y)))
	
	myCov = cov(x,y)
	mySlope = myCov[0,1]/myCov[1,1]
	#print(mySlope)
	return mySlope


#temp = binned_statistic_dd(sample=binned_axes,values=ones(len(arg_axes[0])),bins=(tEdges,eEdges), statistic=t_func)
covxy = binned_statistic_dd(binned_axes,arg_axes,bins=(tEdges,eEdges),statistic=t_func)
#covxy = binned_statistic_dd(binned_axes,dd['acqiris2']*dd['GMD'],bins=(tEdges,eEdges))	#this works
#varxx = binned_statistic_dd(binned_axes,dd['GMD']*dd['GMD'],bins=(tEdges,eEdges))		#this work

