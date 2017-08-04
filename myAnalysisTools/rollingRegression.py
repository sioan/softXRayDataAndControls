from pylab import *
from scipy.signal import savgol_coeffs

#def mySavgol_coeffs(window_length,polyorder,deriv):
#	global x,xMatrix,yEstimatorMatrix

window_length = 51
polyorder = 7

x = arange(-(window_length-1)/2,(window_length-1)/2+1)
xMatrix=ones(len(x))

for i in arange(1,polyorder+1):
	xMatrix = vstack([xMatrix,x**(i)])
x=0+xMatrix

yEstimatorMatrix = dot(x.transpose(),dot(inv(dot(x,x.transpose())),x))

plot(yEstimatorMatrix[int((window_length-1)/2)],'bo')
plot(savgol_coeffs(polyorder=polyorder,window_length=window_length,deriv=0),'r-')

show()

#return yEstimatorMatrix[int((window_length-1)/2)+1]
