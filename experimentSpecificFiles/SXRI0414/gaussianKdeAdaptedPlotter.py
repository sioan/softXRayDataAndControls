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
		

myY = (([100*mean(i*arange(len(i)))/mean(i) for i in Z.transpose()]))
myMedianY = [logNormalFittedMax(i)[1] for i in Z.transpose()]

yCalibrated = 0+Y[0]



def normalize(x,ignoreRange):
	tx = x - mean(x[ignoreRange:])
	return tx/std(tx[ignoreRange:])
	

plot(yCalibrated,normalize(myY[::-1],4)) 
plot(yCalibrated,normalize(myMedianY[::-1],4)) 
plot(myBinCount[1][1][:-1][::-1],normalize(myModes,4)) 
plot(binEdges[1][:-1][::-1],normalize(tempAverage,4))
ylim(-3,2)
xlim(-1,20)
show()
