from pylab import *
from scipy.signal import savgol_coeffs
from scipy.signal import gaussian

window_length = 301
polyorder = 7
bandwidth=10


def mySavgol_coeffs(window_length,polyorder,deriv):
	#global x,xMatrix,yEstimatorMatrix

	#window_length = 51
	#polyorder = 7

	x = arange(-(window_length-1)/2,(window_length-1)/2+1)
	xMatrix=ones(len(x))

	for i in arange(1,polyorder+1):
		xMatrix = vstack([xMatrix,x**(i)])
	x=0+xMatrix

	yEstimatorMatrix = dot(x.transpose(),dot(inv(dot(x,x.transpose())),x))
	
	return yEstimatorMatrix[int((window_length-1)/2)]

def bandwidth_limited(window_length,bandwidth,nPeaks,shift):
	global x,xMatrix,yEstimatorMatrix

	x = gaussian(window_length,bandwidth)
	xMatrix=ones(len(x))
	leftSide = True

	for i in arange(2,2*nPeaks):
		#print(str(x))
	
		if(leftSide==True):
			x=append(0,0+diff(x))
			leftSide = False
		elif(leftSide==False):
			x=append(0+diff(x),0)
			leftSide = True

		xMatrix = vstack([xMatrix,x])


	x=0+xMatrix

	yEstimatorMatrix = dot(x.transpose(),dot(inv(dot(x,x.transpose())),x))

	return yEstimatorMatrix[int((window_length-1)/2)-shift]


#plot(yEstimatorMatrix[int((window_length-1)/2)],'bo')
subplot(221)
plot(mySavgol_coeffs(polyorder=polyorder,window_length=window_length,deriv=0),'bo')
plot(savgol_coeffs(polyorder=polyorder,window_length=window_length,deriv=0),'g-')

subplot(222)
#plot(bandwidth_limited(window_length=window_length,bandwidth=bandwidth,nPeaks=2,shift=0))
#plot(bandwidth_limited(window_length=window_length,bandwidth=bandwidth,nPeaks=4,shift=0))
for i in arange(2,8,2):
	y = abs(fft(bandwidth_limited(window_length=window_length,bandwidth=bandwidth,nPeaks=i,shift=0)))[:int(window_length/2)]
	y/=y[1]
	loglog(y)

subplot(223)
#plot(bandwidth_limited(window_length=window_length,bandwidth=bandwidth,nPeaks=2,shift=0))
#plot(bandwidth_limited(window_length=window_length,bandwidth=bandwidth,nPeaks=4,shift=0))
for i in arange(2,8,2):
	plot(bandwidth_limited(window_length=window_length,bandwidth=bandwidth,nPeaks=i,shift=0))

show()

#return yEstimatorMatrix[int((window_length-1)/2)+1]
