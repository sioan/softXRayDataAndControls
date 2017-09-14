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

myFiles = [ i for i in os.listdir(dataDirectory) if ".pkl" in i]

myDataDict = {}

for i in myFiles:
	myDataDict[i[:-4]] = pickle.load(open(dataDirectory+i,"rb"))


fig, axs = plt.subplots(nrows=1, ncols=1, sharex=True)
#ax = axs[0,0]
ax = axs
ax.set_title('time resolved')

normalizeY(myDataDict)
myCounter = 0
myColor=iter(cm.rainbow(np.linspace(0,1,len(myDataDict.keys()))))

for i in myDataDict:

	thisColor = next(myColor) 

	x = -myDataDict[i]['x']
	y = myDataDict[i]['yMean']-myCounter*75
	yErrorBars = myDataDict[i]['standardDeviation']/myDataDict[i]['counts']**0.5
	ySmoothed = errorWeightedSmoothing(y,yErrorBars,29,3)
		

	ax.errorbar(x,y,yerr=yErrorBars,label=i,marker='o',linestyle='None')
	plot(x,ySmoothed[0],linewidth=4,c='k',linestyle='-')
	myCounter+=1

ax.set_xlabel('time(ps)')
ax.set_ylabel('normalized acqiris')
legend(myDataDict.keys(),loc=0)

show()
