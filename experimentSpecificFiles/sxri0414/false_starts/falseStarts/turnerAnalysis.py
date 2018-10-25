#sxri0414
#laser pulse ~100 fs
#x-ray pulse width is ~60 fs
#jitter ~100 fs
#/reg/neh/home/joshuat/Analysis/i0414
#data sets 59 and 60.  Just 60.
#values are 'apd', 'gmd', and 'timedelaystage', 
#these are the time tools.  only one is correct 'timepos', 'timeneg'
from pylab import *
from scipy.signal import savgol_coeffs
from scipy.signal import savgol_filter

myTime = loadtxt("time.csv")
myError = loadtxt("error.csv")
mySignal= loadtxt("signal.csv")

def errorWeightedSmoothing(myData,myError,myWidth,myOrder):
	myWeights = savgol_coeffs(myWidth,myOrder,0)
	
	
	mySignal = convolve(myData/myError**2,myWeights,mode='same')

	mySignal = mySignal / convolve(1.0/myError**2,myWeights,mode='same')

	myErrors = (1.0/convolve(1.0/myError**2,myWeights,mode='same'))**0.5/sum(myWeights)**0.5

	return mySignal,myErrors


mySmoothedSignal,mySmoothedError = errorWeightedSmoothing(mySignal,myError,23,3)

subplot(121)
errorbar(myTime,mySmoothedSignal,mySmoothedError,linewidth=4,elinewidth=0.2,color='r')
errorbar(myTime,mySignal,myError,marker='o',linewidth=0,elinewidth=0.2)
ylim(0.0034,0.0042)

subplot(122)
#errorbar(myTime,mySignal,myError,marker='o',linewidth=0,elinewidth=0.2)
errorbar(myTime,mySmoothedSignal,mySmoothedError,linewidth=2,elinewidth=0.2)
ylim(0.0034,0.0042)

#savetxt(mySmoothedSignal,mySmoothedError)

show()
