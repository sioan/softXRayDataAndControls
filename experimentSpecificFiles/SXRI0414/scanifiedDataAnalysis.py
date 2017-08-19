from pylab import *
import os

def jackKnifeScan(myData,myError):
	myWeight = nan_to_num(1.0/myErrors)

	averageData = (mean(nan_to_num(myData)*myWeight,axis=0)/mean(myWeight,axis=0))[::-1]

	tempData = 0+averageData
	for i in myData:
		temp = (averageData - nan_to_num(i)*0.01)	
		tempData = vstack([tempData,temp])
		
	return tempData

filePath = "./scanifiedData/"
#fileNames = os.listdir(filePath)

#fileNames = [i for i in os.listdir(filePath) if "Odd" in i]
#fileNames = [i for i in os.listdir(filePath) if "Even" in i]
fileNames = os.listdir(filePath)

myData = loadtxt(filePath+fileNames[0])[:,1]
myErrors = loadtxt(filePath+fileNames[0])[:,2]



for myFile in fileNames[1:]:
	myData = vstack([myData,loadtxt(filePath+myFile)[:,1]])
	myErrors = vstack([myErrors,loadtxt(filePath+myFile)[:,2]])

myWeight = nan_to_num(1.0/myErrors)

averageData = (mean(nan_to_num(myData)*myWeight,axis=0)/mean(myWeight,axis=0))[::-1]

plot(averageData)
