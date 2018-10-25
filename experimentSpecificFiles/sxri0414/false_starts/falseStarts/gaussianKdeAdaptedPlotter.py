def getPolynomialFittedMax(y):
	myWaveForm = 0+y
	lowerRange = 6
	upperRange = 7

	myWaveForm -= mean(myWaveForm)
	myArgMax = argmax(myWaveForm)
	x = arange(len(myWaveForm))-myArgMax
	myFit = polyfit(x[myArgMax-lowerRange:myArgMax+upperRange], myWaveForm[myArgMax-lowerRange:myArgMax+upperRange],4)

	p = poly1d(myFit)
	xTemp = arange(x[myArgMax-lowerRange],x[myArgMax+upperRange],(x[myArgMax+upperRange]-x[myArgMax-lowerRange])/1000.0)
	#plot(x[myArgMax-3:myArgMax+4],p(x[myArgMax-3:myArgMax+4])) 
	#myMax = max(p(x))
	
	#return myFit[-1]	#placing a dictionary here also works
	return myArgMax+xTemp[argmax(p(xTemp))]

def logNormalFittedMax(y):
		myMode= argmax(y)
		myMax =y[myMode]
		x = arange(len(y))
		initGuess = array([myMax,myMode,1])
		popt, pcov = curve_fit(lognorm, x[2:], y[2:],p0=initGuess)
		#plot(x,lognorm(x,*popt))
		#myModes = append(myModes,popt[1])
		#myModeError = append(myModeError,pcov[1,1])
		#mySigma = append(mySigma,popt[2])

		return popt


def quickInterp(y,x):
	x1 = int(x)
	x2 = int(x+0.5)

	y1 = y[x1]
	y2 = y[x2]
	
	interpolatedValue = y1+ (y2-y1)*(x-x1)
	return interpolatedValue
		

myY = array(([mean(i*arange(len(i)))/mean(i) for i in Z.transpose()]))
myStanDev = array(([std(i*arange(len(i)))/mean(i) for i in Z.transpose()]))
myModeY = array([quickInterp(exp(X[:,0]),logNormalFittedMax(i)[1]) for i in Z.transpose()])
#myModeY = array([X[int(exp(logNormalFittedMax(i)[1])),0] for i in Z.transpose()])

#scatterMedian = array([median([i[0] for i in toBeBinned if (i[1]>j and i[1]<j+.1) ]) for j in arange(0,20,0.01)])
	

scatterMedian = array([	median([i[0] for i in toBeBinned if (i[1]>j and i[1]<j+.1) ]) for j in arange(.5,21,.025)])
scatterMedian = array([	median([i[0] for i in toBeBinned if (i[1]>j and i[1]<j+.1) ]) for j in arange(.5,21,.025)])

yCalibrated = 0+Y[0]



def normalize(x,ignoreRange):
	tx = x - mean(x[ignoreRange:])
	return tx/std(tx[ignoreRange:])
	
"""
plot(yCalibrated,normalize(myY[::-1],4),linewidth=2) 
plot(yCalibrated,normalize(myMedianY[::-1],4),linewidth=2) 
plot(myBinCount[1][1][:-1][::-1],normalize(myModes,4)) 
plot(binEdges[1][:-1][::-1],normalize(tempAverage,4))
ylim(-3,2)
xlim(-1,20)
"""

plot(yCalibrated,myY[::-1]+(myStanDev[::-1])**2*3.0/2.0,linewidth=2) 
plot(yCalibrated,myModeY[::-1],linewidth=2)
plot(myBinCount[1][1][:-1][::-1],myModes) 
plot(binEdges[1][:-1][::-1],tempAverage)
show()
