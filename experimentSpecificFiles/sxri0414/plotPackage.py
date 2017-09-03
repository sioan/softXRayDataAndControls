from pylab import *
import pickle
import os
import sys
sys.path.append("/reg/neh/home/sioan/softXRayDataAndControls/myAnalysisTools/")

dataDirectory = "./binnedData/"

myFiles = [ i for i in os.listdir(dataDirectory) if ".pkl" in i]

myDataDict = {}

for i in myFiles:
	myDataDict[i[:-4]] = pickle.load(open(dataDirectory+i,"rb"))
