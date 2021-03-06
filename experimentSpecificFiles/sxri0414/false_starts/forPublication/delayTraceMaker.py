from pylab import *
import h5py
import os
import sys
import IPython
from hdf5_to_dict import hdf5_to_dict
from filterMasks import filterMasks
from scipy.optimize import curve_fit
from plotPackage import errorWeightedSmoothing
#fit's data to log

#load data
experimentRunName = "sxri0414run72"
myFile = experimentRunName+".h5"
myHdf5Object = h5py.File("../smallHdf5Data/"+myFile)
myDataDict = hdf5_to_dict(myHdf5Object)

#createFilter filter
myMask =  filterMasks.__dict__[experimentRunName](myHdf5Object)

#make I vs I0 calibration
xScatter = myDataDict['GMD'][myMask]
yScatter = myDataDict['acqiris2'][myMask]
maxXScatter = max(xScatter)
myBins = arange(0,maxXScatter,0.000010)
y,x = histogram(xScatter,myBins,weights = yScatter )
nonZeroMask = (y!=0)
y/=(histogram(xScatter,myBins)[0])+1e-9
x = x[nonZeroMask]
y = y[nonZeroMask]
#myFit = polyfit(x,y,4)
myFit = polyfit(append(x,zeros(1e6)),append(y,zeros(1e6)),4)
p = poly1d(myFit)

#correct the time
timeToolSign = 1
myOffset = min(myDataDict['delayStage'])

#myDataDict['TSS_OPAL/pixelTime'] = append(0,myDataDict['TSS_OPAL/pixelTime'])[:-1]
myDataDict['TSS_OPAL/pixelTime'] = append(myDataDict['TSS_OPAL/pixelTime'],[0])[1:]
correctedTimeScatter = (2/.3*(myDataDict['delayStage']-myOffset)+timeToolSign*myDataDict['TSS_OPAL/pixelTime']/1000.0)[myMask]
#correctedTimeScatter -= min(correctedTimeScatter)
figure(0)
plot(xScatter,yScatter,'.')
plot(x,p(x),linewidth=3)

def func(x,a):
	return p(a*x)

#def fitMyData(xdata,ydata):
def fitMyData(binStart,binEnd):

	binStep = binEnd-binStart
	timeMask = correctedTimeScatter>binStart 
	timeMask *= correctedTimeScatter<binEnd
	xdata = xScatter[timeMask]
	ydata = yScatter[timeMask]
	tdata = correctedTimeScatter[timeMask]

	myLength = len(ydata)
	#remove outliers
	#outlier threshold is 20%
	threshold = 0.40/4
	try:
		#threshold = 10.0/(myLength)
		temp=1
	except ZeroDivisionError:
		return -999,-999
	
	ySortedIndex = argsort(ydata)
	ydata = ydata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	xdata = xdata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	tdata = tdata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	
	xSortedIndex = argsort(xdata)
	ydata = ydata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	xdata = xdata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	tdata = tdata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]

	try:
		mySigma = binStep/(binStep+tdata-binStart)**0.5 # equals one if tdata is binStart and  
		#popt, pcov = curve_fit(func, xdata, ydata,p0=1,sigma=mySigma)
		popt, pcov = curve_fit(func, xdata, ydata,p0=1)
	
	except:
		popt,pcov = [-999],[[-999]]

	if popt[0]!=-999:
		#IPython.embed()
		temp = 1

	#IPython.embed()
	return popt[0],pcov[0][0]*len(tdata)**0.5

#binSize = 0.15
binStart= -25.00
binSize = 0.05
myBins = arange(binStart,45,binSize)
myDelayTrace = array([fitMyData(i,i+binSize) for i in myBins])

zeroCountMask = myDelayTrace[:,0]>0
myDelayTrace = myDelayTrace[zeroCountMask]
myBins = myBins[zeroCountMask]
#myBins = myBins[::-1]
myBins *=-1
freqBins = arange(0,1.0/binSize,1/binSize/len(myBins))

figure(1)
#plot(myBins,myDelayTrace[:,0]+0.1)
ySmoothed = errorWeightedSmoothing(myDelayTrace[:,0],myDelayTrace[:,1],29,3)
errorbar(myBins,myDelayTrace[:,0],yerr=myDelayTrace[:,1])
errorbar(myBins,ySmoothed[0],ySmoothed[1],c='k')


preLaser = 10
mySize = myDelayTrace.shape[0]
myNoiseSpectrum = zeros(mySize)
#print len(myNoiseSpectrum)
for i in arange(1,100,preLaser):
	noiseTrace = append(myDelayTrace[-preLaser-i:-i,0]-mean(myDelayTrace[-preLaser-i:-i,0]),zeros(mySize-preLaser))
	myNoiseSpectrum += abs(fft(noiseTrace))**2


myWienerFilter = 1.0/(1+100*myNoiseSpectrum)

#wienerFilteredSignal = real(ifft(myWienerFilter*fft(myDelayTrace[:,0])))
#error weighted wiener filter
wienerFilteredSignal = convolve(real(ifft(myWienerFilter))[:20],1.0/myDelayTrace[:,1]**2*myDelayTrace[:,0],mode='Same')
wienerFilteredSignal /= convolve(real(ifft(myWienerFilter))[:20],1.0/myDelayTrace[:,1]**2,mode='Same')
wienerFilterErrorBars = 1.0/(convolve(real(ifft(myWienerFilter))[:20],1.0/myDelayTrace[:,1]**2,mode='Same'))

#while testing so not overwriting old data
exportData = h5py.File('temp.h5', 'w')	

exportData.create_dataset("time_ps", data=myBins, chunks=True, maxshape=(None,))
exportData.create_dataset("normalized_intensity", data=myDelayTrace[:,0], chunks=True, maxshape=(None,))
exportData.create_dataset("normalized_intensity_error", data=myDelayTrace[:,1], chunks=True, maxshape=(None,))
exportData.create_dataset("wiener_filtered_signal", data=wienerFilteredSignal, chunks=True, maxshape=(None,))
exportData.create_dataset("wiener_filtered_error", data=wienerFilterErrorBars, chunks=True, maxshape=(None,))
exportData.close()


figure(2)
#errorbar(myBins,wienerFilteredSignal,wienerFilterErrorBars)
plot(myBins,wienerFilteredSignal)
show()
