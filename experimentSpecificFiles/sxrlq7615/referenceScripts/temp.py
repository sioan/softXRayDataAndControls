from pylab import *
import psana
from ImgAlgos.PyAlgos import photons
from scipy.signal import convolve2d

runNum = sys.argv[1]

#ds = psana.DataSource('exp=xpptut15:run=340')	#test data from AMO runs 10, 15, and 19
ds = MPIDataSource('exp=xpptut15:run='+str(runNum))
psana.DetNames()

det = psana.Detector('pnccdFront')				#for LQ76 and test amo data
#det = psana.Detector('andor')				#for sxrm2316

yTotal = 0
imgTotal = 0

roiKeyList = ["scatterRegion1","scatterRegion2","scatterRegion3","scatterRegion4","scatterRegion5","scatterRegion6"]

roiRegionCoordinate = {}
#repeat five more time for 6 scattering regions
roiRegionCoordinate["scatterRegion1"] = [[10,20],[10,20]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion2"] = [[20,30],[20,30]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion3"] = [[30,40],[30,40]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion4"] = [[40,20],[40,50]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion5"] = [[50,60],[50,60]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion6"] = [[60,500],[60,500]] #[[xStart,xFinish],[yStart,yFinish]]

numberOfPixelsInROI = 0

for myKey in roiKeyList:
	[xROI, yROI] = roiRegionCoordinate[myKey]
	numberOfPixelsInROI += (xROI[1]-xROI[0])*(yROI[1]-yROI[0])


def twoPulseAmplitudeIn20Percent(myEvt):
	return False
	
	
myRoiDImage = {}

maxNumberOfPhotonsPerImage = 10e5
onePhotonCountBins= zeros([maxNumberOfPhotonsPerImage])
onePhotonCountSquaredBins= zeros([maxNumberOfPhotonsPerImage])

twoPhotonCountBins= zeros([maxNumberOfPhotonsPerImage])
twoPhotonCountSquaredBins= zeros([maxNumberOfPhotonsPerImage])

threePhotonCountBins= zeros([maxNumberOfPhotonsPerImage])
threePhotonCountSquaredBins= zeros([maxNumberOfPhotonsPerImage])


for nevent,evt in enumerate(ds.events()):
	try:
		# includes pedestal subtraction, common-mode correction, bad-pixel
		# suppresion, and returns an "unassembled" 3D array of cspad panels
		#calib_array = det.calib(evt)
		# this is the same as the above, but also uses geometry to
		# create an "assembled" 2D image (including "fake pixels" in gaps)
		
		#boiler plate code
		calib = det.calib(evt)	#not used for andor, only for pnccd.  at least as of 5/22/2017
		if calib is None: continue	#not used for andor, only for pnccd.  at least as of 5/22/2017
		
		#this is for pnccd	
		img = det.image(evt)

		#this is for andor
		#img = det.raw_data(evt) - det.pedestals(evt)
		
		#savetxt("xpptut15Run"+str(nevent),img)
		#imgTotal += img

		y,x = histogram(img.flatten(),bins=arange(0,20000,1))
		yTotal += y

		#check if two pulses heights are within 20%.  also need to deconvolute.
		if twoPulseAmplitudeIn20Percent(evt): continue

		
		#convert camera counts to photon counts 
		nphotons_nda = det.photons(evt,adu_per_photon=2000)
		myImage = det.image(evt,nphotons_nda)
		imgTotal += myImage

		#maskout non ROI region.  (i.e. set to zero)
		imageROId = 0 * myImage
		for myKey in roiKeyList:
			[xROI, yROI] = roiRegionCoordinate[myKey]
			
			imageROId[xROI[0]:xROI[1],yROI[0]:yROI[1]] += myImage[xROI[0]:xROI[1],yROI[0]:yROI[1]]

		totalPhotonCount = sum(imageROId)
			


		#merging three commented out sections above into a single section
		totalPhotonsPerPixel = sum(imageROId) *1.0/ numberOfPixelsInROI			#x-axis
		onePhotonEventsPerPixel =  sum((imageROId==1).astype(int))*1.0/numberOfPixelsInROI			#one of the y-axes
		twoPhotonEventsPerPixel = sum((imageROId==2).astype(int))*1.0/numberOfPixelsInROI			#one of the y-axes
		threePhotonEventsPerPixel = sum((imageROId==3).astype(int))*1.0/numberOfPixelsInROI			#one of the y-axes
		fourPhotonEventsPerPixel = sum((imageROId==4).astype(int))*1.0/numberOfPixelsInROI			#one of the y-axes

		if (nevent % 10==1):
			
			myString = str("%d event number has accumulated %f" %(nevent,totalPhotonsPerPixel))
			print myString

		#forming the graphs that will be used for determining final product
		

		onePhotonCountBins[totalPhotonCount]+= onePhotonEventsPerPixel
		onePhotonCountSquaredBins[totalPhotonCount]+= onePhotonEventsPerPixel**2

		twoPhotonCountBins[totalPhotonCount]+= twoPhotonEventsPerPixel
		twoPhotonCountSquaredBins[totalPhotonCount]+= twoPhotonEventsPerPixel**2

		threePhotonCountBins[totalPhotonCount]+= threePhotonEventsPerPixel
		threePhotonCountSquaredBins[totalPhotonCount]+= threePhotonEventsPerPixel**2


		#toExport = array([onePhotonEventsPerPixel,twoPhotonEventsPerPixel,threePhotonEventsPerPixel,fourPhotonEventsPerPixel,totalPhotonsPerPixel])
		
		except KeyboardInterrupt:
			break

myString = "xpptut15:run="+str(runNum)
savetxt(myString,array([onePhotonCountBins,twoPhotonCountBins,threePhotonCountBins]).transpose())
