from pylab import *
from scipy.signal import savgol_coeffs
from scipy.signal import convolve2d 

myTime = loadtxt("time.csv")
myError = loadtxt("error.csv")
mySignal= loadtxt("signal.csv")

mySize = 240
mySigX = arange(mySize)*2e-6+.0037

myMap = zeros([mySize])

for i in arange(mySignal.shape[0]):
	temp = mySignal[i]*exp(-(mySigX-mySignal[i])**2/(2*myError[i]**2))
	myMap = vstack([myMap,temp])


myKernel = exp(-(arange(-4,5)*0.1)**2/(2*.2**2))
myKernel = vstack([myKernel,zeros(myKernel.shape[0])])

myResult = convolve2d(myMap.transpose(),myKernel)[::-1]
myResult = clip(myResult,0.002,1000)

subplot(211)

imshow(myResult,cmap='magma')

my2dPlot = zeros(209)

for i in arange(209):
	my2dPlot[i] = sum(arange(mySize+1)*myResult[:,i])/sum(myResult[:,i])

subplot(212)
plot(-my2dPlot[4:-4],linewidth=4)
#twinx()
#plot(loadtxt("signal.csv"),'ro')

show()
