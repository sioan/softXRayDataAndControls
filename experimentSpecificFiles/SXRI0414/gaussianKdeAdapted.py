from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

def measure(n):
	print("Measurement model, return two coupled measurements.")
	m1 = np.random.normal(size=n)
	m2 = np.random.normal(scale=0.5, size=n)
	return m1+m2, m1-m2

#m1, m2 = measure(2000)
normalizedAcqiris = myDict['acqiris2']/myDict['GMD'] 
#m1,m2 = normalizedAcqiris[myMask], myDict['delayStage'][myMask]
m1,m2 = normalizedAcqiris[myMask], myDict['estimatedTime'][myMask]
xmin = m1.min()
xmax = m1.max()
ymin = m2.min()
ymax = m2.max()
print("Perform a kernel density estimate on the data:")

X, Y = np.mgrid[xmin:xmax:200j, ymin:ymax:200j]
positions = np.vstack([X.ravel(), Y.ravel()])
values = np.vstack([m1, m2])
kernel = stats.gaussian_kde(values)
Z = np.reshape(kernel(positions).T, X.shape)

execfile("gaussianKdeAdaptedPlotter.py")

"""
print("Plot the results:")


#fig, ax = plt.subplots()
#ax.imshow(np.rot90(Z), cmap=plt.cm.gist_earth_r,extent=[xmin, xmax, ymin, ymax])
#ax.plot(m1, m2, 'k.', markersize=2)
#ax.set_xlim([xmin, xmax])
#ax.set_ylim([ymin, ymax])
#plt.show()

def getPolynomialFittedMax(y):
	myWaveForm = 0+y

	myWaveForm -= mean(myWaveForm)
	myArgMax = argmax(myWaveForm)
	x = arange(len(myWaveForm))-myArgMax
	myFit = polyfit(x[myArgMax-3:myArgMax+4], myWaveForm[myArgMax-3:myArgMax+4],4)

	p = poly1d(myFit)
	xTemp = arange(x[myArgMax-3],x[myArgMax+4],(x[myArgMax+4]-x[myArgMax-3])/100.0)
	#plot(x[myArgMax-3:myArgMax+4],p(x[myArgMax-3:myArgMax+4])) 
	#myMax = max(p(x))
	
	#return myFit[-1]	#placing a dictionary here also works
	return myArgMax-xTemp[argmax(p(xTemp))]

#myY = (([100*mean(i*arange(len(i)))/mean(i) for i in Z.transpose()]))
myY = [getPolynomialFittedMax(i) for i in Z.transpose()]

yCalibrated = 0+Y[0]



def normalize(x,ignoreRange):
	tx = x - mean(x[ignoreRange:])
	return tx/std(tx[ignoreRange:])
	

plot(yCalibrated,normalize(myY[::-1],4)) 
plot(myBinCount[1][1][:-1][::-1],normalize(myModes,4)) 
plot(binEdges[1][:-1][::-1],normalize(tempAverage,4))
ylim(-3,2)
xlim(-1,20)
show()"""
