from pylab import *

myClimMax=10

#subplot(121)
#imshow(myHistogramPositiveTimeTotal,aspect=yEdges.shape[0]*1.0/xEdges.shape[0],clim=(0,myClimMax),cmap='magma',extent=[yEdges[0],yEdges[-1],xEdges[0],xEdges[-1]])
imshow(myHistogramPositiveTimeTotal,aspect=xEdges.shape[0]*1.0/yEdges.shape[0],clim=(0,myClimMax),cmap='magma',extent=[yEdges[0],yEdges[-1],xEdges[0],xEdges[-1]])


#subplot(122)
#imshow(myHistogramNegativeTimeTotal,aspect=0.5*yEdges.shape[0]*1.0/xEdges.shape[0],clim=(0,myClimMax),cmap='magma',extent=[yEdges[0],yEdges[-1],xEdges[0],xEdges[-1]])


#plot(xEdges,(mean(1.0*myHist*cumsum(ones(myHist.shape),axis=1),axis=1)),'o')
#mean(1.0*myHist,axis=1).shape),'o'



show()
