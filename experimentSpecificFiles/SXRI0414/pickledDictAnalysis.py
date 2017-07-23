from pylab import *
from scipy.odr import *
import pickle
from scipy import interpolate
from scipy.signal import savgol_filter
from scipy.stats.stats import pearsonr

myData = pickle.load(open("dictifiedData.pkl","rb"))

#calibrate linearity
x,y=loadtxt("linearityAnalysis.dat")
y=y[argsort(x)]
x=x[argsort(x)]
lower,upper = 21,561
interpolatedCalibrationFunction = interpolate.interp1d(x[lower:upper], savgol_filter(y[lower:upper],31,1))

def linearModel(B,x):
        return B[0]*x
linear = Model(linearModel)

#median truncation
medTrunc = .025
usedCount = 350

correlationList = array([])
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
		x = interpolatedCalibrationFunction(x)*1

		#median truncation along y
		#x=x[argsort(y)][round(x.shape[0]*medTrunc):-round(x.shape[0]*medTrunc)]
		#y=y[argsort(y)][round(y.shape[0]*medTrunc):-round(y.shape[0]*medTrunc)]


		#median truncation along x
		y=y[argsort(x)][round(y.shape[0]*medTrunc):-round(y.shape[0]*medTrunc)]
		x=x[argsort(x)][round(x.shape[0]*medTrunc):-round(x.shape[0]*medTrunc)]

		#y=y[argsort(x)][round(y.shape[0]/2)-usedCount:round(y.shape[0]/2)+usedCount]
		#x=x[argsort(x)][round(x.shape[0]/2)-usedCount:round(x.shape[0]/2)+usedCount]


		bruteDivide = append(bruteDivide,mean(y*1.0/x))
		totalCounts = append(totalCounts,y.shape[0])

		rawX = append(rawX,mean(x))
		rawY = append(rawY,mean(y))


		
		tempHistogram = histogram(y/x,bins=arange(-1.01,3.01,.01))[0]
		if(sum(tempHistogram)!=0):

			if(my2dHistogram!=None):
				my2dHistogram = vstack([my2dHistogram, tempHistogram])
			else:
				my2dHistogram =  tempHistogram


		y=y-mean(y)
		x=x-mean(x)
		
		dataForODR = RealData(x,y)
		myODR = ODR(dataForODR, linear, beta0=[0.01])
		myOdrOutput=myODR.run()
	
		correlationList = append(correlationList,myOdrOutput.beta[0])	
		#correlationList = append(correlationList,pearsonr(x,y)[1])
		correlationErrorList = append(correlationErrorList,myOdrOutput.sd_beta[0])

		myTime = append(myTime,float(thisKey))


	except:
		continue

subplot(221)
plot(myTime,bruteDivide,'.')

subplot(222)
plot(myTime,correlationList,'.')
#ylim(.9,1.2)

subplot(223)
plot(myTime,totalCounts,'b.')

subplot(224)
plot(myTime,(correlationErrorList),'.')
#ylim(0.1,0.15)

show()
