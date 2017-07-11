"""
#from skbeam.core.accumulators.binned_statistic import RadialBinnedStatistic, RPhiBinnedStatistic
from PIL import Image
from pylab import *
import psana
dsource = psana.MPIDataSource('exp=sxrlq2715:run=156')
pnccdDetectorObject = psana.Detector('pnccd')



myEnumeratedEvents = enumerate(dsource.events())
eventNumber,thisEvent = next(myEnumeratedEvents)

for eventNumber,thisEvent in myEnumeratedEvents:
	if eventNumber == 270:
		break



y,x = histogram((pnccdDetectorObject.image(thisEvent)).flatten(),bins=arange(0,2000,1))
plot(x[1:],log(1+y))
print eventNumber
show()

#myMask = (array(Image.open("mask.tiff"))+1)%2
myMask = array(Image.open("mask.tiff"))
temp = pnccdDetectorObject.photons(thisEvent,adu_per_photon=220)
myImage = pnccdDetectorObject.image(thisEvent,temp)

#rphibinstat = RPhiBinnedStatistic(img.shape, bins=(3,1), statistic='sum', origin=(0,0), range = ((0,2),(0,np.pi/3)))

#rphibinstat = RPhiBinnedStatistic(myImage.shape, bins=(30,1), statistic='sum', origin=(522,512), range = ((147,2),(177,6.28318)), mask = myMask)
"""
myTheta = zeros(360)
myThetaPixelCount = zeros(360)
myCenter = [512,521]
myOuterRadius = 70
myInnerRadius = 60

for x in arange(myCenter[0]-myOuterRadius,myCenter[0]+myOuterRadius):
	for y in arange(myCenter[1]-myOuterRadius,myCenter[1]+myOuterRadius):
		theta = (round(180*angle((x-myCenter[0])+1j*(y-myCenter[1]))/3.14159)+360)%360
		r = ((x-myCenter[0])**2+(y-myCenter[1])**2)**0.5
		if(r>myInnerRadius and r<myOuterRadius):
			#print "ok"
			myTheta[theta] = myTheta[theta] + myImage[x,y]
			myThetaPixelCount[theta] = myThetaPixelCount[theta] + 1.0*myMask[x,y]
			#print theta
myTheta = nan_to_num(myTheta/myThetaPixelCount)
subplot(211)
plot(myTheta)
subplot(212)

myRandConvolution = zeros(myTheta.shape[0])
myRand = rand(myTheta.shape[0])

myConvolution = zeros(myTheta.shape[0])
for i in arange(myTheta.shape[0]):
	myConvolution[i] = sum(myTheta*roll(myTheta,i))
	myRandConvolution[i] = sum(myRand*roll(myRand,i))
plot(roll(myConvolution,180),'b-')
#twinx()
#plot(roll(myRandConvolution,180),'r-')
show()
