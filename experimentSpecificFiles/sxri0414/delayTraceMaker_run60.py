from pylab import *
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

#load data
experimentRunName = "sxri0414run60"
myFile = experimentRunName+".h5"
myHdf5Object = h5py.File("smallHdf5Data/"+myFile)
myDataDict = hdf5_to_dict(myHdf5Object)

#createFilter filter
myMask =  filterMasks.__dict__[experimentRunName](myHdf5Object)

#make I vs I0 calibration
xScatter = myDataDict['GMD'][myMask]
yScatter = myDataDict['acqiris2'][myMask]
energyScatter = myDataDict['ebeam/photon_energy'][myMask]
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

timeOffsetError=1
#myDataDict['TSS_OPAL/pixelTime'] = append(zeros(timeOffsetError),myDataDict['TSS_OPAL/pixelTime'])[:-timeOffsetError]
#myDataDict['TSS_OPAL/pixelTime'] = append(myDataDict['TSS_OPAL/pixelTime'],zeros(timeOffsetError))[timeOffsetError:]
correctedTimeScatter = (2/.3*(myDataDict['delayStage']-myOffset)+timeToolSign*myDataDict['TSS_OPAL/pixelTime']/1000.0)[myMask]
#correctedTimeScatter -= min(correctedTimeScatter)
figure(0)
plot(xScatter,yScatter,'.')
plot(x,p(x),linewidth=3)

def func(x,a):
	return p(a*x)

def getPhotonEnergyCalibration(startEnergy,stopEnergy,stepEnergy):
	
	#startEnergy,stopEnergy,stepEnergy = 911,918,0.4
	myBins = arange(startEnergy,stopEnergy,stepEnergy)

	toReturn = [0,0]
	for i in myBins:
		#print i
		tempMask = 0+myMask
		tempMask *= myDataDict['ebeam/photon_energy']>i
		tempMask *= myDataDict['ebeam/photon_energy']<(i+stepEnergy)
		tempMask = tempMask.astype(bool)

		#IPython.embed()

		x =  myDataDict['GMD'][tempMask]
		y =  myDataDict['acqiris2'][tempMask]

		myCov = cov(x,y)
		

		toReturn = vstack([toReturn,[i,myCov[0,1]/myCov[0,0]]])

	return toReturn[1:].transpose()

#temp = getPhotonEnergyCalibration(913,923,0.4)
temp = getPhotonEnergyCalibration(910,918,0.4)
myInterpolatedCalibration = interp1d(temp[0],temp[1],kind='linear',bounds_error=False,fill_value='extrapolate')


def fitMyData(binStart,binEnd):

	binStep = binEnd-binStart
	timeMask = correctedTimeScatter>binStart 
	timeMask *= correctedTimeScatter<binEnd
	xdata = xScatter[timeMask]
	ydata = yScatter[timeMask]
	tdata = correctedTimeScatter[timeMask]
	edata = energyScatter[timeMask]
	
	#energy calibration
	#ydata = ydata/(myInterpolatedCalibration(913)/myInterpolatedCalibration(edata))

	myLength = len(ydata)
	#remove outliers
	#outlier threshold is 20%
	threshold = 0.00/4
	try:
		#threshold = 10.0/(myLength)
		temp=1
	except ZeroDivisionError:
		return -999,-999
	
	#sorting for median filtering
	ySortedIndex = argsort(ydata)
	ydata = ydata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	xdata = xdata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	tdata = tdata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	edata = edata[ySortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	
	xSortedIndex = argsort(xdata)
	ydata = ydata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	xdata = xdata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	tdata = tdata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]
	edata = edata[xSortedIndex][int(threshold*myLength):int(myLength*(1-1*threshold))]

	try:
		mySigma = binStep/(binStep+tdata-binStart)**0.5 # equals one if tdata is binStart and weighted binning by distance from edge of bin
		#popt, pcov = curve_fit(func, xdata, ydata,p0=1,sigma=mySigma) #implementing the weight
		#popt, pcov = curve_fit(func, xdata, ydata,p0=1)
		#IPython.embed()
		myTempCov = cov([xdata,ydata,edata])
		xMat = array([ones(len(xdata)),xdata,edata]).transpose()
		#myResults =  lstsq(xMat,ydata)
		#myResults = dot(dot(inv(dot(xMat.transpose(),xMat)),xMat.transpose()),ydata)

		#popt,pcov = [[myResults[2]],[[-9999]]]
			
		popt,pcov = [myTempCov[0,1]/myTempCov[0,0]],[[myTempCov[0,0]/len(edata)]]	#hey this works on run 60! needs more agressive filtering 
		#in filter file. also, see 1.6745 THz oscillation right after pulse.  Is this artifact?
		#popt,pcov = [myTempCov[2,1]/myTempCov[2,2]],[[myTempCov[2,2]/len(edata)]]
		
	except:
		popt,pcov = [-999],[[-999]]

	if popt[0]!=-999:
		#IPython.embed()
		temp = 1

	#IPython.embed()
	return popt[0],pcov[0][0]*len(tdata)**0.5

#binSize = 0.15
binStart= -25.15
binSize = 0.075
myBins = arange(binStart,45,binSize)
myDelayTrace = array([fitMyData(i,i+binSize) for i in myBins])

zeroCountMask = myDelayTrace[:,0]>0
#zeroCountMask = myDelayTrace[:,0]>-9999
myDelayTrace = myDelayTrace[zeroCountMask]
myBins = myBins[zeroCountMask]
#myBins = myBins[::-1]
myBins *=-1
freqBins = arange(0,1.0/binSize,1/binSize/len(myBins))

figure(1)
#plot(myBins,myDelayTrace[:,0]+0.1)
ySmoothed = errorWeightedSmoothing(myDelayTrace[:,0],myDelayTrace[:,1],29,3)
errorbar(myBins,myDelayTrace[:,0],yerr=myDelayTrace[:,1])
#errorbar(myBins,ySmoothed[0],ySmoothed[1],c='k')


preLaser = 4
mySize = myDelayTrace.shape[0]
myNoiseSpectrum = zeros(mySize)
#print len(myNoiseSpectrum)
for i in arange(10,100,preLaser):
	noiseTrace = append(myDelayTrace[-preLaser-i:-i,0]-mean(myDelayTrace[-preLaser-i:-i,0]),zeros(mySize-preLaser))
	myNoiseSpectrum += abs(fft(noiseTrace))**2


#myWienerFilter = 1.0/(1+100*myNoiseSpectrum)
transferSpectrum = 1
myWienerFilter = transferSpectrum/(transferSpectrum+.01*myNoiseSpectrum)# the myNoiseSpectrum coefficient is arbitrary. how to choose in physically meaningful way?

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
errorbar(myBins,myDelayTrace[:,0],yerr=myDelayTrace[:,1])
#plot(myBins,myDelayTrace[:,0])
plot(myBins[7:],wienerFilteredSignal[:-7],c='k',linewidth=3)
#plot(myBins,wienerFilteredSignal)
show()
