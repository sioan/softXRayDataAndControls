import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import pickle
import os
import sys

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
for i in myDataDict:
	x = -myDataDict[i]['x']
	y = myDataDict[i]['yMean']-myCounter*100
	yErrorBars = myDataDict[i]['standardDeviation']/myDataDict[i]['counts']**0.5

	ax.errorbar(x,y,yerr=yErrorBars,label=i,marker='o')
	myCounter+=1

ax.set_xlabel('time(ps)')
ax.set_ylabel('normalized acqiris')
legend(myDataDict.keys(),loc=0)

show()
