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
#plots according to instructions in config file directory
#
#==================


import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import pickle
import os
import sys
from scipy.signal import savgol_coeffs
import h5py
from hdf5_to_dict import hdf5_to_dict
from ConfigParser import ConfigParser
config = ConfigParser()
config.read('config/plotting.cfg')


def errorWeightedSmoothing(myData,myError,myWidth,myOrder):
	myWeights = savgol_coeffs(myWidth,myOrder,0)
	
	
	mySignal = convolve(myData/myError**2,myWeights,mode='same')

	mySignal = mySignal / convolve(1.0/myError**2,myWeights,mode='same')

	myErrors = (1.0/convolve(1.0/myError**2,myWeights,mode='same'))**0.5/sum(myWeights)**0.5

	return mySignal,myErrors

def normalizeY(myDataDict):
	for i in myDataDict:
		#myDataDict[i]['standardDeviation']-= mean(myDataDict[i]['yMean'][-50:-30])
		myDataDict[i]['yMean']-= mean(myDataDict[i]['yMean'][-50:-30])
		myDataDict[i]['yMean']+= 500


sys.path.append("/reg/neh/home/sioan/softXRayDataAndControls/myAnalysisTools/")

dataDirectory = os.getcwd()+"/binnedData/"

myFiles = [ i for i in os.listdir(dataDirectory) if ".h5" in i]

myDataDict = {}

for i in myFiles:
	print i
	#myDataDict[i[:-4]] = pickle.load(open(dataDirectory+i,"rb"))
	myDataDict[i[:-3]] = hdf5_to_dict(h5py.File(dataDirectory+i,"r"))


config._sections

myFigureDictionary = {}

for i in config._sections['figureList']:
	if i=="__name__": continue
	print i

	myFigureDictionary[i] = {}

	myFigureDictionary[i]['fig'], myFigureDictionary[i]['axs'] = plt.subplots(nrows=1, ncols=1, sharex=True)
	myFigureDictionary[i]['axs'].set_title('time resolved')

	normalizeY(myDataDict)
	myCounter = 0
	myFigureDictionary[i]['myColor']=iter(cm.rainbow(np.linspace(0,1,len(myDataDict.keys()))))


for i in myDataDict:

	figureNumber = config._sections[i]['figurenumber']

	thisColor = next(myFigureDictionary[figureNumber]['myColor']) 

	x = myDataDict[i]['x']
	x-=max(x)
	x*=-1
	
	y = myDataDict[i]['yMean']-myCounter*75
	yErrorBars = myDataDict[i]['standardDeviation']/myDataDict[i]['counts']**0.5
	ySmoothed = errorWeightedSmoothing(y,yErrorBars,29,3)
		

	myFigureDictionary[figureNumber]['axs'].errorbar(x,y,yerr=yErrorBars,label=i,marker='o',linestyle='None')
	myFigureDictionary[figureNumber]['axs'].plot(x,ySmoothed[0],linewidth=4,c='k',linestyle='-')
	myCounter+=1

#ax.set_xlabel('time(ps)')
#ax.set_ylabel('normalized acqiris')
#legend(myDataDict.keys(),loc=0)

show()
