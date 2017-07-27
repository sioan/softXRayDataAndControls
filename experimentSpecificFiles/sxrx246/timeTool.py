from pylab import *
import psana
from psmon.plots import Image,XYPlot
from psmon import publish
import pandas 
import time
import os

#import TimeTool
psana.setOption('psana.calib-dir','/reg//d/psdm/sxr/sxrx24615/calib')
#myDataSource = psana.DataSource("shmem=psana.0:stop=no")
myDataSourcepsana.DataSource('exp=sxrx24615:run=22')

#not necessarily online.
#ttOptions = TimeTool.AnalyzeOptions(get_key='TSS_OPAL',eventcode_nobeam = 162)	#162 event is bykick

#ttAnalyze = TimeTool.PyAnalyze(ttOptions)
#ds = psana.DataSource(self.datasource, module=ttAnalyze)

#tssOpalROI = [[xStart,xEnd],[yStart,yEnd]]
tssOpalROI = [[1,-1],[1,-1]]
#opal1ROI = [[1,-1],[1,-1]]
opal1ROI = loadtxt("myConfig.dat")
myConfigLastModTime = os.path.getatime("myConfig.dat")
#opal1SecondROI = [[1,-1],[1,-1]]
tssAxis,opal1Axis = [1,1]
correlationWindow = 31

myConfig=loadtxt("myConfig.dat")

tssOpalDetectorObject = psana.Detector("TSS_OPAL")
opal1DetectorObject = psana.Detector("OPAL1")
evrDetectorObject = psana.Detector("evr0")

byKickTssOpalProfile = zeros(10)
byKickOpal1Profile = zeros(10)

myEnumeratedEvents = enumerate(myDataSource.events())
for nEvent, thisEvent in myEnumeratedEvents:

	if(myConfigLastModTime != os.path.getatime("myConfig.dat")):
		opal1ROI = loadtxt("myConfig.dat").astype(int)[:2]
		tssOpalROI = loadtxt("myConfig.dat").astype(int)[2:4]		#[[620,-370],[100,-1]] is the main signal, [[680,-270],[100,-1] is reference
		tssAxis,opal1Axis = loadtxt("myConfig.dat").astype(int)[4] 
		correlationWindow = loadtxt("myConfig.dat").astype(int)[5][0] 
		os.system("touch myConfig.dat")
		myConfigLastModTime = os.path.getatime("myConfig.dat")
		print "new kernel"

	time.sleep(0.01)

	#ttResults = ttAnalyze.process(evt)
	#evr = evrDet[1].eventCodes(evt)
	theseEventCodes = evrDetectorObject.eventCodes(thisEvent)
	
	tssOpalImage = tssOpalDetectorObject.image(thisEvent)
	tempTss = 0+ tssOpalImage
	tssOpalImage=tssOpalImage[tssOpalROI[0][0]:tssOpalROI[0][1],tssOpalROI[1][0]:tssOpalROI[1][1]]
	opal1Image = opal1DetectorObject.image(thisEvent)[opal1ROI[0][0]:opal1ROI[0][1],opal1ROI[1][0]:opal1ROI[1][1]]
	
	
	if any([None is k for k in [tssOpalImage,opal1Image]]):
		continue

	tssProfile = sum(tssOpalImage,axis=tssAxis)
	opal1Profile = sum(opal1Image,axis=opal1Axis)
	if (nEvent%5==1):
		tssOpalPublishedImage = Image(0,"TSS_OPAL",tssOpalImage)
		publish.send('TSS_OPAL',tssOpalPublishedImage)

		opal1PublishedImage = Image(0,"OPAL1",opal1Image)
		publish.send('OPAL1',opal1PublishedImage)


	if 162 in theseEventCodes:
		byKickTssOpalProfile = 0 + tssProfile
		byKickOpal1Profile = 0 + opal1Profile
		byKickOpal1Image = 0+ opal1Image
		print("got bY kick "+str(nEvent))
		
		continue


	#tssCorrelation = array(pandas.rolling_corr(pandas.Series(byKickTssOpalProfile),pandas.Series(tssProfile),21))
	#opal1Correlation = array(pandas.rolling_corr(pandas.Series(opal1Profile),pandas.Series(byKickOpal1Profile),21))
	#tssCorrelation = array(pandas.Series(byKickTssOpalProfile).rolling(window=correlationWindow).corr(pandas.Series(tssProfile)))
	#opal1Correlation = array(pandas.Series(opal1Profile).rolling(window=correlationWindow).corr(pandas.Series(byKickOpal1Profile)))

	#opal1Subtraction = opal1Profile - 

	#tssPublishedProfile = XYPlot(0,"TSS_OPAL_Profile",arange(len(tssCorrelation)),tssCorrelation)
	#publish.send('TSS_OPAL_Profile',tssPublishedProfile)

	#tssPublishedProfile = XYPlot(0,"TSS_OPAL_Profile",arange(len(byKickTssOpalProfile)),byKickTssOpalProfile)
	#publish.send('TSS_OPAL_Profile',tssPublishedProfile)
	try:
		tempCov = cov(tssProfile,byKickTssOpalProfile)
		temp = tssProfile-tempCov[0,1]/tempCov[1,1]*(byKickTssOpalProfile-mean(byKickTssOpalProfile))
		temp -= mean(temp)
		temp2 = (arange(len(temp))-len(temp)/2.0)**2
		temp -= dot(temp,temp2)/dot(temp2,temp2)*temp2
		
		if (nEvent%5==1):
			tssPublishedProfile2 = XYPlot(0,"TSS_OPAL_Profile",arange(len(tssProfile)),temp)
			publish.send('TSS_OPAL_Profile',tssPublishedProfile2)
	except:
		print("skipping")


	#opal1PublishedProfile = XYPlot(0,"OPAL1_Profile",arange(len(opal1Correlation)),opal1Correlation)
	#publish.send('OPAL1_Profile',opal1PublishedProfile)
	try:
		temp = mean((opal1Image-byKickOpal1Image)[:73,:],axis=0)
		temp-=mean(temp)
	
		temp2 = mean(opal1Image[73:,:],axis=0)
		temp2-=mean(temp2)

		#temp = temp - dot(temp,temp2)/dot(temp2,temp2)*temp2
		#temp = 
		if (nEvent%5==1):
			opal1PublishedProfile = XYPlot(0,"OPAL1_Profile",arange(len(temp)),temp)
			publish.send('OPAL1_Profile',opal1PublishedProfile)
	except:
		print("skipping")

