from pylab import *
def rollingCovariance(scatterData,axisToAverage,axisToBin,bins,m,isLog=False):
	#myKernel = stats.gaussian_kde(toBeBinned[:,0])x


	#movingMean = array([	median([i[0] for i in scatterData if (i[1]>j and i[1]<j+.1) ]) for j in arange(.5,21,.025)])
	#movingMedian = array([	median([i[0] for i in scatterData if (i[1]>j and i[1]<j+.1) ]) for j in arange(.5,21,.025)])
	
	stepSize = mean(list(set(diff(bins))))

	rebins = arange(bins[0],bins[-1]+2*stepSize,stepSize*1.0/m)

	movingStatistics = array([cov(array([i for i in scatterData if (i[axisToBin]>j and i[axisToBin]<j+stepSize) ]).transpose()) for j in rebins])

	return rebins,movingStatistics

#execution
#import rollingCovariance
#reload(rollingCovariance)
#x,y = rollingCovariance.rollingCovariance(toBeBinned,0,1,arange(0.5,21,.2),2,isLog=True)
#x,y = rollingCovariance.rollingCovariance(toBeBinned,0,1,arange(0.5,21,.25),50,isLog=True)
#myCov = [i[0,1] for i in y[:-200]]
#plot(x[:3940],myCov[:3940],'.')
#freq = arange(3940)*1.0/max(x:3940)
plot(freq,log(abs(fft([:3940]))))

