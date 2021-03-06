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
from lib.hdf5_to_dict import hdf5_to_dict
from filterMasks import filterMasks
from scipy.optimize import curve_fit
from lib.analysis_library import errorWeightedSmoothing
from scipy.interpolate import interp1d
from lib.analysis_library import vectorized_binned_statistic_dd
#fit's data to log

def normalize(data_dict):
	temp_dict = {}
	for i in data_dict:
		temp_dict[i] = 0+nan_to_num(data_dict[i])

	for i in data_dict:
		for j in arange(data_dict[i].shape[1]):
			temp_dict[i][:,j]-= mean(temp_dict[i][:,j])
			temp_dict[i][:,j]/= std(temp_dict[i][:,j])
			temp_dict[i][:,j]+=5*j*std(temp_dict[i][:,j])

	return temp_dict

def plot_dict(to_graph_dict):
	#u,s,v = svd(covxy[0])
	myCounter = 0
	myFigureDictionary={}
	for i in to_graph_dict:
		myFigureDictionary[i]={}
		myFigureDictionary[i]['fig'], myFigureDictionary[i]['axs'] = plt.subplots(nrows=1, ncols=1, sharex=True)
		#figure(myCounter)
		myFigureDictionary[i]['axs'].set_title(i)
		myCounter+=1
		for j in arange(to_graph_dict[i].shape[1]):
			#plot(-1*tEdges[:-1],sum(covxy[0],axis=1))
			myFigureDictionary[i]['axs'].plot(-1*tEdges[:-1],to_graph_dict[i][:,j])
			

	show()

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
	simple_slope = myCov[0,1]/myCov[0,0]
	
	non_serialized_result = array([mean(y*1.0/x),mean(y)/mean(1.0*x),simple_slope])
	#serialized_result = pickle.dumps(non_serialized_result)
	dict_result = {'shot_by_shot_median':median(y*1.0/x),'shot_by_shot':mean(y*1.0/x),'median':median(y)/median(1.0*x),'averaged':mean(y)/mean(1.0*x),'simple_slope':simple_slope}

	#IPython.embed()
	return dict_result

def s_func(r):
	temp = array([pickle.loads(i) for i in r])
	print(temp.shape)
	return 1


if __name__ == '__main__':

	#load data
	TOP=""
	experimentRunName = "sxri0414run60"
	myFile = experimentRunName+".h5"
	myHdf5Object = h5py.File(TOP+"smallHdf5Data/"+myFile,"r")
	myDataDict = hdf5_to_dict(myHdf5Object)

	#createFilter filter
	myMask =  filterMasks.__dict__[experimentRunName](myHdf5Object)


	#make I vs I0 calibration
	dd = apply_filter(myDataDict,myMask)
	binned_axes = array([dd['atm_corrected_timing'],dd['ebeam/photon_energy']]).transpose()
	arg_axes = array([dd['GMD'],dd['acqiris2']]).transpose()
	#arg_axes = array([pickle.dumps(i) for i in array([dd['GMD'],dd['acqiris2']]).transpose()])	#17 seconds on run 60.
	tEdges = arange(327,346.5,0.075)
	#eEdges = arange(900,930,0.25)
	#eEdges = append(append(900,arange(912.5,916.5,.5)),920)
	eEdges = array([900,912.5,914.5,916.5,920])
	

	#covxy = binned_statistic_dd(binned_axes,arg_axes,bins=(tEdges,eEdges),statistic=t_func)
	covxy = vectorized_binned_statistic_dd(binned_axes,arg_axes,bins=(tEdges,eEdges),statistic=t_func)
	 
	plot_dict(normalize(covxy))



