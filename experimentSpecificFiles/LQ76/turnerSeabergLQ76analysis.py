from pylab import *
import psana
from ImgAlgos.PyAlgos import photons
from scipy.signal import convolve2d

#runNum = sys.argv[1]
runNum = "38"

#ds = psana.DataSource('exp=xpptut15:run=340')	#test data from AMO runs 10, 15, and 19
#ds = psana.DataSource('exp=sxrm2316:run=103')	#real data from specified experiment (sxrm2316)
#ds = psana.DataSource('exp=sxrlq7615:run='+runNum)
ds = psana.MPIDataSource('exp=sxrlq7615:run='+runNum+':smd')
#ds = psana.MPIDataSource('exp=xpptut15:run='+str(runNum))

#psana.DetNames()
aquiris2 = psana.Detector("Acq01")

det = psana.Detector('pnccd')				#for LQ76 and test amo data
#det = psana.Detector('andor')				#for sxrm2316

smldata = ds.small_data('run'+str(runNum)+'.h5')

yTotal = 0
imgTotal = 0
#stackOfROIImagesForMatt = []

roiKeyList = ["scatterRegion1","scatterRegion2","scatterRegion3"]#,"scatterRegion4","scatterRegion5","scatterRegion6"]

roiRegionCoordinate = {}
#repeat five more time for 6 scattering regions
roiRegionCoordinate["scatterRegion1"] = [[340,440],[369,469]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion2"] = [[300,400],[540,640]] #[[xStart,xFinish],[yStart,yFinish]]
roiRegionCoordinate["scatterRegion3"] = [[440,580],[440,580]] #[[xStart,xFinish],[yStart,yFinish]]
#roiRegionCoordinate["scatterRegion4"] = [[40,20],[40,50]] #[[xStart,xFinish],[yStart,yFinish]]
#roiRegionCoordinate["scatterRegion5"] = [[50,60],[50,60]] #[[xStart,xFinish],[yStart,yFinish]]
#roiRegionCoordinate["scatterRegion6"] = [[60,500],[60,500]] #[[xStart,xFinish],[yStart,yFinish]]

numberOfPixelsInROI = 0

for myKey in roiKeyList:
	[xROI, yROI] = roiRegionCoordinate[myKey]
	numberOfPixelsInROI += (xROI[1]-xROI[0])*(yROI[1]-yROI[0])


def twoPulseAmplitudeIn20Percent(myEvt):
	
	y,x = aquiris2(myEvt)
	x=x[0]
	y=y[0]

	return True
	
	
myRoiDImage = {}
myRoiHistogram = {}

maxNumberOfPhotonsPerImage = 10e5
onePhotonCountBins= zeros([maxNumberOfPhotonsPerImage])
onePhotonCountSquaredBins= zeros([maxNumberOfPhotonsPerImage])

twoPhotonCountBins= zeros([maxNumberOfPhotonsPerImage])
twoPhotonCountSquaredBins= zeros([maxNumberOfPhotonsPerImage])

threePhotonCountBins= zeros([maxNumberOfPhotonsPerImage])
threePhotonCountSquaredBins= zeros([maxNumberOfPhotonsPerImage])

averageCalib = 0
nphotons_ndaAverage = 0

for nevent,evt in enumerate(ds.events()):
	
	if (nevent > 100): break
	
	try:
		d = {}

		# includes pedestal subtraction, common-mode correction, bad-pixel
		# suppresion, and returns an "unassembled" 3D array of cspad panels
		#calib_array = det.calib(evt)
		# this is the same as the above, but also uses geometry to
		# create an "assembled" 2D image (including "fake pixels" in gaps)
		
		#boiler plate code
		calib = det.calib(evt)	#not used for andor, only for pnccd.  at least as of 5/22/2017
		if calib is None: continue	#not used for andor, only for pnccd.  at least as of 5/22/2017
		
		#this is for pnccd	
		#img = det.image(evt)
		img = hstack([vstack([calib[0],calib[3]]),vstack([calib[1],calib[2]])])
		#averageCalib+= calib
		
		#this is for andor
		#img = det.raw_data(evt) - det.pedestals(evt)
		
		#savetxt("xpptut15Run"+str(nevent),img)
		#imgTotal += img

		y,x = histogram(img.flatten(),bins=arange(0,20000,1))
		yTotal += y

		#check if two pulses heights are within 20%.  also need to deconvolute.
		if not twoPulseAmplitudeIn20Percent(evt): continue

		
		#convert camera counts to photon counts 
		nphotons_nda = det.photons(evt,adu_per_photon=1250)
	

		nphotons_ndaAverage +=nphotons_nda

		#myImage = det.image(evt,nphotons_nda)
		myImage = hstack([vstack([nphotons_nda[0],nphotons_nda[1][::-1,::-1]]),vstack([nphotons_nda[3],nphotons_nda[2][::-1,::-1]])])
		imgTotal += myImage

		#this is for mseaberg
		#stackOfROIImagesForMatt.append(nphotons_nda[0][350:450,350:450])
		

		#maskout non ROI region.  (i.e. set to zero)
		imageROId = 0 * myImage

		for myKey in roiKeyList:
			d[myKey]["onePhotonCountBins"] = zeros(5000)
			d[myKey]["twoPhotonCountBins"] = zeros(5000)
			d[myKey]["threePhotonCountBins"] = zeros(5000)
			d[myKey]["fourPhotonCountBins"] = zeros(5000)

		for myKey in roiKeyList:
			d[myKey] = {}
			[xROI, yROI] = roiRegionCoordinate[myKey]
			
			imageROId = myImage[xROI[0]:xROI[1],yROI[0]:yROI[1]]

			totalPhotonsPerPixel = int(sum(imageROId) *1.0)					#x-axis
			onePhotonEventsPerPixel =  sum((imageROId==1).astype(int))*1.0			#one of the y-axes
			twoPhotonEventsPerPixel = sum((imageROId==2).astype(int))*1.0
			threePhotonEventsPerPixel = sum((imageROId==3).astype(int))*1.0
			fourPhotonEventsPerPixel = sum((imageROId==4).astype(int))*1.0			#one of the y-axes

			d[myKey]["onePhotonCountBins"][totalPhotonCount] += onePhotonEventsPerPixel
			d[myKey]["twoPhotonCountBins"][totalPhotonCount] += twoPhotonEventsPerPixel
			d[myKey]["threePhotonCountBins"][totalPhotonCount] += threePhotonEventsPerPixel
			d[myKey]["fourPhotonCountBins"][totalPhotonCount] += fourPhotonEventsPerPixel
			
			

		#merging three commented out sections above into a single section
		#totalPhotonsPerPixel = sum(imageROId) *1.0/ numberOfPixelsInROI			#x-axis

		if (nevent % 10==1):
			
			myString = str("%d event number has accumulated %f" %(nevent,totalPhotonsPerPixel))
			print myString

		#forming the graphs that will be used for determining final product


		#toExport = array([onePhotonEventsPerPixel,twoPhotonEventsPerPixel,threePhotonEventsPerPixel,fourPhotonEventsPerPixel,totalPhotonsPerPixel])

		smldata.event(d)

	except KeyboardInterrupt:
		break

#myString = "sxrlq7615:run=38.txt"
#savetxt(myString,array([onePhotonCountBins,twoPhotonCountBins,threePhotonCountBins]).transpose())
#savetxt("myImage.txt",)
smldata.save()
