from pylab import *
from scipy.odr import *
import pickle
from scipy import interpolate
from scipy.signal import savgol_filter
from scipy.stats.stats import pearsonr
import sys
from scipy.signal import savgol_filter

runNumber = sys.argv[1]
myData = pickle.load(open("dictifiedDataRun"+str(runNumber)+".pkl","rb"))

#calibrate linearity
x,y=loadtxt("linearityAnalysis.dat")
y=y[argsort(x)]
x=x[argsort(x)]
lower,upper = 21,561
interpolatedCalibrationFunction = interpolate.interp1d(x[lower:upper], savgol_filter(y[lower:upper],31,1))

#median truncation
medTrunc = .020
medTruncBias = 0.00
med2Trunc = 200

myCorrelationList = array([])
correlationErrorList = array([])
bruteDivide = array([])
myTime = array([])
totalCounts = array([])
rawX = array([])
rawY = array([])
my2dHistogram = None


for thisKey in myData.keys():

	try:
		x,y = myData[thisKey][1:,:].transpose()

		x = interpolatedCalibrationFunction(x)*1.0

		#median truncation along x
		#y=y[argsort(x)][round(y.shape[0]*(medTrunc-medTruncBias)):-round(y.shape[0]*(medTrunc+medTruncBias))]
		#x=x[argsort(x)][round(x.shape[0]*(medTrunc-medTruncBias)):-round(x.shape[0]*(medTrunc+medTruncBias))]
		y=y[argsort(x)][round(y.shape[0]/2-med2Trunc):round(y.shape[0]/2+med2Trunc)]
		x=x[argsort(x)][round(x.shape[0]/2-med2Trunc):round(x.shape[0]/2+med2Trunc)]
		
		
		temp= y/x
	
		#x=x[argsort(temp)][round(x.shape[0]*(medTrunc-medTruncBias)):-round(x.shape[0]*(medTrunc+medTruncBias))]
		#y=y[argsort(temp)][round(y.shape[0]*(medTrunc-medTruncBias)):-round(y.shape[0]*(medTrunc+medTruncBias))]
		

		#temp = mean(sort(y*1.0/x)[med2Trunc:-med2Trunc])		
		#bruteDivide = append(bruteDivide,temp)
		#totalCounts = append(totalCounts,temp.shape[0]-2*med2Trunc)
		
		bruteDivide = append(bruteDivide,mean(y*1.0/x))
		totalCounts = append(totalCounts,y.shape[0])

		rawX = append(rawX,mean(x))
		rawY = append(rawY,mean(y))

		myCov = cov(x,y)
		#pearsonr(y,x)[0]
		myCorrelation = myCov[0,1]/(myCov[1,1]*myCov[0,0])**0.5
		#myOffset = 
	
		myCorrelationList = append(myCorrelationList,myCorrelation)
		correlationErrorList = append(correlationErrorList,log(pearsonr(y,x)[1]))

		myTime = append(myTime,float(thisKey))

		xLast = 0+x
		yLast =	0+y	


	except KeyboardInterrupt:
		continue

	except IndexError:
		print("key "+thisKey+" had an error")
		continue

myTime -= max(myTime)
myTime*=-2*0.299792458
sortedIndex = argsort(myTime)

myTime = myTime[sortedIndex]
bruteDivide = bruteDivide[sortedIndex]
myCorrelationList = myCorrelationList[sortedIndex]
totalCounts = totalCounts[sortedIndex]
rawX=rawX[sortedIndex]
rawY=rawY[sortedIndex]

subplot(221)
plot(myTime,savgol_filter(bruteDivide,11,5),'.')
#twinx()
#plot(myTime,totalCounts,'r.')

subplot(222)
plot(myTime,myCorrelationList,'.')
#ylim(.9,1.2)

subplot(223)
plot(myTime,rawY*1.0/rawX,'.')
#ylim(0.1,0.15)

subplot(224)
plot(myTime,totalCounts,'r.')

#ylim(400,1300)


show()
