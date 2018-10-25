from pylab import *
import h5py
from scipy.optimize import curve_fit

f = h5py.File("binnedData/sxri0414run60.h5","r")

x = array(f['x'])
x-=max(x)
x*=-1
y = array(f['yMean'])

yErrorBars = array(f['standardDeviation'])/array(f['counts'])**0.5

errorbar(x,y,yerr=yErrorBars,marker='o',linestyle='None',c='r')
ylim(720,860)

#needs to provide vector of residuals for scipy least squares. not for curve fit
def myFitEquation(x,*p0):

	offset,tau1,tau2,a1,a2,f,phi = p0
	#offset,t1,t2,t3,a1,a2,a3,f,phi = p0
	
	t = x
	#return offset+a1*exp(-t/tau1)+a2*exp(-t/tau2)*sin(2*pi*f*t+phi)*cos(2*pi*f*t+phi)/(cos(2*pi*f*t+phi)**2+0.25)
	#return offset+a1*exp(t/tau1)+a2*exp(-t/tau2)*sin(2*pi*f*t+phi)
	return offset+a1/((t-t1)**2+1)+a2/((t-t2)**2+1)+a3/((t-t3)**2+1)


#myLeastSquaresResult = least_squares(myFitEquation,myFitParameters)

#p0 = [860,5,5,-50,75,0.15,+0.4] for sinusoid

plot(x[:165],myFitEquation(x[:165],*p0),c='k',linewidth=3)

popt, pcov = curve_fit(myFitEquation, x[:165], y[:165], p0, sigma=yErrorBars[:165], absolute_sigma=True)

plot(x[:165],myFitEquation(x[:165],*popt),c='b',linewidth=3)



f.close()
