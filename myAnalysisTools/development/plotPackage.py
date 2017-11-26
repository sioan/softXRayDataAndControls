#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/ipython -i

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
from lib.hdf5_to_dict import hdf5_to_dict
from ConfigParser import ConfigParser
config = ConfigParser()
config.read('config/plotting.cfg')


def normalizeY(myDataDict):
	for i in myDataDict:
		#myDataDict[i]['standardDeviation']-= mean(myDataDict[i]['yMean'][-50:-30])
		myDataDict[i]['yMean']-= mean(myDataDict[i]['yMean'][-50:-30])
		myDataDict[i]['yMean']+= 500

myDataDict = {}
if __name__ == '__main__':
	#global myDataDict
	sys.path.append("/reg/neh/home/sioan/softXRayDataAndControls/myAnalysisTools/")

	dataDirectory = os.getcwd()+"/binnedData/"

	myFiles = [ i for i in os.listdir(dataDirectory) if ".h5" in i]

	myDataDict = {}

	for i in myFiles:
		print(i)
		#myDataDict[i[:-4]] = pickle.load(open(dataDirectory+i,"rb"))
		myDataDict[i[:-3]] = hdf5_to_dict(h5py.File(dataDirectory+i,"r"))


	config._sections

	myFigureDictionary = {}

	for i in config._sections['figureList']:
		if i=="__name__": continue
		#print i

		myFigureDictionary[i] = {}

		myFigureDictionary[i]['fig'], myFigureDictionary[i]['axs'] = plt.subplots(nrows=1, ncols=1, sharex=True)
		myFigureDictionary[i]['axs'].set_title('time resolved')

		normalizeY(myDataDict)
		myCounter = 0
		myFigureDictionary[i]['myColor']=iter(cm.rainbow(np.linspace(0,1,len(myDataDict.keys()))))

		myFigureDictionary[i]['axsTwin']=myFigureDictionary[i]['axs'].twinx()

	tempSize = 300
	temp = zeros(tempSize)

	for i in myDataDict:
	
		figureNumber = config._sections[i]['figurenumber']
	
		#thisColor = next(myFigureDictionary[figureNumber]['myColor'])
		thisColor = config._sections[i]['color']  

		x = myDataDict[i]['x']
		x-=max(x)
		x*=-1
	
		y = myDataDict[i]['yMean']-myCounter*75
		yErrorBars = myDataDict[i]['standardDeviation']/myDataDict[i]['counts']**0.5
		ySmoothed = errorWeightedSmoothing(y,yErrorBars,29,3)
		print(i)
		if (i=='sxri0414run72' or i=='sxri0414run81'):
			mySizeDiff =tempSize-len(ySmoothed[0])
			temp=vstack([temp,append(ySmoothed[0],zeros(mySizeDiff))])

		if ('twinx' in config._sections[i]):
			myFigureDictionary[figureNumber]['axsTwin'].errorbar(x,y,yerr=yErrorBars,label=i,marker='o',linestyle='None',c=thisColor)
			#myFigureDictionary[figureNumber]['axsTwin'].plot(x,ySmoothed[0],linewidth=4,c=thisColor,linestyle='-')
			myFigureDictionary[figureNumber]['axsTwin'].plot(x,ySmoothed[0],linewidth=4,c='k',linestyle='-')

		else:
			myFigureDictionary[figureNumber]['axs'].errorbar(x,y,yerr=yErrorBars,label=i,marker='o',linestyle='None',c=thisColor)
			#myFigureDictionary[figureNumber]['axs'].plot(x,ySmoothed[0],linewidth=4,c=thisColor,linestyle='-')
			myFigureDictionary[figureNumber]['axs'].plot(x,ySmoothed[0],linewidth=4,c='k',linestyle='-')
			#myFigureDictionary[figureNumber]['axs'].errorbar(x,ySmoothed[0],ySmoothed[1],linewidth=1,c='k',linestyle='-')
		myCounter+=1

	myFigureDictionary['figure0']['axs'].set_ylabel("amplitude")
	myFigureDictionary['figure0']['axs'].set_xlabel("time(ps)")
	myFigureDictionary['figure0']['axs'].legend()
	myLines, myLabels = myFigureDictionary['figure1']['axs'].get_legend_handles_labels()
	myLinesT, myLabelsT = myFigureDictionary['figure1']['axsTwin'].get_legend_handles_labels()

	myFigureDictionary['figure1']['axs'].set_ylabel("amplitude")
	myFigureDictionary['figure1']['axs'].set_xlabel("time(ps)")
	myFigureDictionary['figure1']['axs'].legend(myLines+myLinesT,myLabels+myLabelsT)

	show()
