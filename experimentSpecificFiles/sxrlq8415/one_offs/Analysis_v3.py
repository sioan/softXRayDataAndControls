import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import time
from pylab import *
import h5py
import scipy as sci
import scipy.io as io
from scipy.optimize import leastsq
runNums=[13]#Make sure they're comma sepearated eg: [112,113]
Nbins = 30
save=0 #1 for save, 0 for no save

#V2: 
#Switching to delayEpics (Positive Reading issue)

#Select Analysis Mode, 
#0: 800&IR, single MCT delay scan
#1: 800 & IR , Reflectivity (Time Scan)
#2: 800 & Xray
#3: XAS spectrum
#4: Theta Scan (MCP)
#5: Theta Scan (APDNOAP) 
#6: Time Scan Xray & 800
#7: Asimuth Scan (APDNOAP)
#8: 800 & Xray TIME SCAN
#10: pulse duration

Mode = 5

plt.ion()


Sig = []
GMD = []
MCP = []
delay = []
laserMoving = []
laserOn = []
laserOff = []
eventNum = []
bykik = []

DelayEnc = []
DelayEpics = []
LaserDiode = []

Sample_Theta = []
Sample_Flip = []
Detector_2theta = []
Detector_Flip = []
I0 = []

PhaseCavity_t1 = []
PhaseCavity_t2 = []
waveplate = []
energy = []
Reflec = []
photon_energy = []
pulse_duration = []


MCT1 = []
MCPI0 = []
APDNOAP = []
APDAP =[]

gratingEpics = []

for run in runNums: 
	#Data File, .npz file
	data = h5py.File('sxrlq8415run'+str(run)+'.h5')
	# Pull data into Vectors
	Acq01 = data['Acq01']
	MCPI0 = array(Acq01['MCPI0'])	
	LargeAPD = array(Acq01['APDNOAP'])
	SmallAPD = array(Acq01['APDAP'])
	Sample_Theta = array(data['Sample_Theta'])
	Detector_Flip = array(data['Detector_Flip'])
	EventCodes = data['evr']
	laserOn = array(EventCodes['code_76'])
	laserOff = array(EventCodes['code_77'])
	DelayEnc = array(data['DelayEnc']['DLS_PS'])

if Mode == 1: 
	Sig = MCT1
	I0 = MCT2
if Mode == 2: 
	Sig = MCP
	I0 = MCPI0
if Mode == 3: 
	Sig = APDNOAP
	I0 = MCPI0
if Mode == 4: 
	Sig = MCP
	I0 = MCPI0
if Mode == 5:
	Sig = -LargeAPD
	I0 = -MCPI0
	
if Mode == 6:
	Sig = MCP
	I0 = MCPI0
	Mode = 1
if Mode == 7:
	Sig = -LargeAPD
	I0 = -MCPI0
	Sample_Theta = Detector_Flip
	Mode = 5

if Mode == 8: 
	Sig = -LargeAPD
	I0 = -MCPI0
	Mode = 1

if Mode == 9 or Mode == 10:
	Sig = APDNOAP
	I0 = MCPI0


# filter out bad shots
if 1==0:
	mask = np.logical_and(I0<888,I0<887)

	#mask=np.logical_and(np.logical_and(np.logical_and(np.logical_and(np.logical_and(np.logical_and(np.logical_and(np.logical_and(np.logical_not(np.isnan(PhaseCavity_t2)),np.logical_not(np.isnan
	#LaserDiode[mask]
	I0_OG = I0
	Sig = Sig[mask]
	#GMD = GMD[mask]
	#MCP = MCP[mask]
	I0 = I0[mask]
	#delay = delay[mask] 
	DelayEnc = DelayEnc[mask]
	#LaserDiode = LaserDiode[mask]
	#gratingEpics = gratingEpics[mask]
	#energy = energy[mask]
	Sample_Theta = Sample_Theta[mask]
	laserOn = laserOn[mask]
	#PhaseCavity_t2 = PhaseCavity_t2[mask]
	#PhaseCavity_t1 = PhaseCavity_t1[mask]
	#photon_energy = photon_energy[mask]
	#pulse_duration = pulse_duration[mask]
	#DelayEnc = DelayEnc-PhaseCavity_t2
	#waveplate = waveplate[mask]

# Normalize Pre-bin? 

Sig=Sig/I0

# sort data
if Mode == 1 or Mode == 8: 
	ind = np.argsort(DelayEnc)
if Mode == 2: 
	ind = np.argsort(delay)
if Mode == 3: 
	ind = np.argsort(energy) 
if Mode == 4 or Mode == 5: 
	ind = np.argsort(Sample_Theta)
if Mode == 9: 
	ind = np.argsort(waveplate)
if Mode == 10:
	ind = np.argsort(pulse_duration)

#Sort data wrt to Delay, Theta, etc.

Sig = Sig[ind]
Sample_Theta = Sample_Theta[ind]
#GMD = GMD[ind]
I0 = I0[ind]
#delay = delay[ind]
DelayEnc = DelayEnc[ind]
#LaserDiode = LaserDiode[ind]
#energy = energy[ind]
#gratingEpics = gratingEpics[ind]
laserOn = laserOn[ind]
#PhaseCavity_t2=PhaseCavity_t2[ind]
#photon_energy=photon_energy[ind]
#pulse_duration=pulse_duration[ind]

N = np.size(DelayEnc)

#Setup Delay ends
if Mode == 1 or Mode == 8:
	delayMin = np.amin(DelayEnc)
	delayMax = np.amax(DelayEnc)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	N = np.size(DelayEnc)
if Mode == 2: 
	delayMin = np.amin(delay)
	delayMax = np.amax(delay)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	N = np.size(delay)
if Mode == 3: 
	delayMin = np.amin(energy)
	delayMax = np.amax(energy)	
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	N = np.size(photon_energy)
if Mode == 4 or Mode == 5: 
	delayMin = np.amin(Sample_Theta)
	delayMax = np.amax(Sample_Theta)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	binCenters = np.unique(Sample_Theta)
	Nbins = len(binCenters)
	N = np.size(Sig)
if Mode == 9:
	delayMin = np.amin(waveplate)
	delayMax = np.amax(waveplate)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	#N = np.size(delay)
if Mode == 10:
	delayMin = np.amin(pulse_duration)
	delayMax = np.amax(pulse_duration)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	N = np.size(pulse_duration)

SigBinOn = np.zeros(Nbins)
SigBinOff = np.zeros(Nbins)
I0BinOn = np.zeros(Nbins)
I0BinOff = np.zeros(Nbins)

SigOnSquared = np.zeros(Nbins)
SigOffSquared = np.zeros(Nbins)
I0OnSquared = np.zeros(Nbins)
I0OffSquared = np.zeros(Nbins)

NormedOn = np.zeros(Nbins)
NormedOff = np.zeros(Nbins)
NormOnSquared = np.zeros(Nbins)
NormOffSquared = np.zeros(Nbins)

NormReflec = np.zeros(Nbins)
NormReflecSq = np.zeros(Nbins)

counterOn = np.zeros(Nbins)
counterOff = np.zeros(Nbins)

BK_APDNOAP = np.zeros(Nbins)
BK_APDAP = np.zeros(Nbins)

for i in range(N):
	# find bin number

	#currDelay = delay[i]
	if Mode == 1: 
		currDelay = DelayEnc[i]	
	if Mode == 2: 
		currDelay = delay[i]
	if Mode == 3: 
		currDelay = energy[i]
	if Mode == 4 or Mode == 5: 
		currDelay = Sample_Theta[i]
	if Mode == 9:
		currDelay = waveplate[i]
	if Mode == 10:
		currDelay = pulse_duration[i]

	#sometimes an issue where delayMax and delayMin == nan if DelayEnc = [nan, nan, ...]
	binNum = np.int((currDelay-delayMin)/(delayMax-delayMin)*(Nbins)) #replaced floor() with int() to cast to ints
	if binNum == Nbins:
		binNum = Nbins - 1	
	
	# MODES With Laser On / Laser Off distiction
	if Mode == 1 or Mode == 2 or Mode == 8 or Mode == 5 or Mode == 10: 
		if laserOn[i]==1:
		#if LaserDiode[i]==1:
			SigBinOn[binNum] += Sig[i]
			I0BinOn[binNum] += I0[i]
			NormedOn[binNum] += Sig[i]/I0[i]
			counterOn[binNum] += 1

			SigOnSquared[binNum] += Sig[i]**2
			I0OnSquared[binNum] += I0[i]**2
			NormOnSquared[binNum] += (Sig[i]/I0[i])**2
			

		elif laserOn[i]==0:
		#elif LaserDiode[i]==0:
			SigBinOff[binNum] += Sig[i]
			I0BinOff[binNum] += I0[i]
			NormedOff[binNum] += Sig[i]/I0[i]
			counterOff[binNum] += 1

			SigOffSquared[binNum] += Sig[i]**2
			I0OffSquared[binNum] += I0[i]**2
			NormOffSquared[binNum] += (Sig[i]/I0[i])**2
		if 1 == 0:
			
			BK_APDNOAP[binNum] += APDNOAPBK[i]
			BK_APDAP[binNum] += APDAPBK[i]


	if Mode == 3 or Mode == 4 or Mode == 51: 
	 		SigBinOn[binNum] += Sig[i]
			I0BinOn[binNum] += I0[i]
			NormedOn[binNum] += Sig[i]/I0[i]
			counterOn[binNum] += 1

			SigOnSquared[binNum] += Sig[i]**2
			I0OnSquared[binNum] += I0[i]**2
			NormOnSquared[binNum] += (Sig[i]/I0[i])**2
			if 1 == 0:
				BK_APDNOAP[binNum] += APDNOAPBK[i]
				BK_APDAP[binNum] += APDAPBK[i]

NormedOn = NormedOn/counterOn
NormedOff = NormedOff/counterOff

NormDiff = NormedOn-NormedOff

NormOnSquared = NormOnSquared/counterOn
NormOffSquared = NormOffSquared/counterOff

NormDiffSq = NormOnSquared-NormOffSquared

SigBinOn = SigBinOn/counterOn
SigBinOff = SigBinOff/counterOff
I0BinOn = I0BinOn/counterOn
I0BinOff = I0BinOff/counterOff

SigOnSquared = SigOnSquared/counterOn
SigOffSquared = SigOffSquared/counterOff
I0OnSquared = I0OnSquared/counterOn
I0OffSquared = I0OffSquared/counterOff

SigOnVar = SigOnSquared - SigBinOn**2
SigOffVar = SigOffSquared - SigBinOff**2
I0OnVar = I0OnSquared - I0BinOn**2
I0OffVar = I0OffSquared - I0BinOff**2
NormOnVar = NormOnSquared - NormedOn**2
NormOffVar = NormOffSquared - NormedOff**2
NormDiffVar = NormDiffSq - NormDiff**2

OnError = np.sqrt(SigOnVar*np.abs(1/I0BinOn)**2 + I0OnVar*np.abs(SigBinOn/I0BinOn**2)**2)/np.sqrt(counterOn)
OffError = np.sqrt(SigOffVar*np.abs(1/I0BinOff)**2 + I0OffVar*np.abs(SigBinOff/I0BinOff**2)**2)/np.sqrt(counterOff)

OnError = np.sqrt(NormOnVar)/np.sqrt(counterOn)
OffError = np.sqrt(NormOffVar)/np.sqrt(counterOff)
DiffError = np.sqrt(NormDiffVar)/np.sqrt(counterOn+counterOff)

#SigBinOn = SigBinOn/I0BinOn
#SigBinOff = SigBinOff/I0BinOff

if Mode == 0:
	plt.figure()
	plt.hist(DelayEnc,100)
	plt.title('Histogram of Delay Stage Runs:%s, NumBins:%s' %(runNums,Nbins))
	plt.xlabel('Delay, [ps]')
	
	plt.figure()
	plt.plot(binCenters,SigBinOn)
	plt.title('Delay Scan, MCT signal Runs:%s, NumBins:%s' %(runNums,Nbins))
	plt.xlabel('Delay [ps]')
	plt.show(block=True)


if Mode == 8: 
	plt.figure()
	plt.errorbars(binCenters, SigBinOn, yerr=OnError, fmt='o-')
	plt.errorbars(binCenters, SigBinOff, yerr=OffError, fmt='o-')
	plt.title('Time Scan. Runs:%s, NumbBins:%s' %(runNums,Nbins))
	plt.xlabe('Delay [ps]')


if Mode == 1 & 1==1:
	#Reflec = (SigBinOn/I0BinOn - SigBinOff/I0BinOff)/(SigBinOff/I0BinOff)
	#Reflec = np.divide((SigBinOn - SigBinOff),SigBinOff)
	Reflec = (SigBinOn-np.mean(SigBinOff))/np.mean(SigBinOff)
	#Reflec =(NormedOn - NormedOff)/NormedOff
	#Reflec=Reflec[~np.isnan(Reflec)]
	plt.figure()
	plt.hist(DelayEnc,100)
        plt.title('Histogram of Delay Stage')
        plt.xlabel('Delay, [ps]')

        plt.figure()
        plt.plot(binCenters,Reflec,'ko-')
	plt.plot(binCenters,SigBinOn,'bo-')
	plt.plot(binCenters,SigBinOff,'ro-')
	#plt.errorbar(binCenters, SigBinOff, yerr=OffError, fmt='o-')
	#plt.ylabel('Delta_R/R')
        plt.title('Time Scan Runs:%s, NumBins:%s' %(runNums,Nbins))
        plt.xlabel('Delay [ps]')

	plt.show(block=True)

	#fig,ax =plt.subplots()
	#plt.errorbar(binCenters, SigBinOn, yerr=OnError, fmt='o-')
        #plt.errorbar(binCenters, SigBinOff, yerr=OffError, fmt='o-')

	#ax.plot(binCenters,SigBinOn, label='Laser On')
	#ax.plot(binCenters,SigBinOff, label= 'Laser off')
	#plt.title(' Indiv. traces. Runs:%s, NumBins:%s' %(runNums,Nbins))
	#legend = ax.legend(loc='upper left',shadow=True)
	#plt.show(block=True)


	#plt.figure()
	#plt.plot(binCenters,s)
	#plt.show(block=True)
	#legend = ax.legend.get_frame()

#if Mode == 2:
	
		
if Mode == 3: 
	print SigBinOn
	plt.figure()
	plt.plot(binCenters, SigBinOn)
	plt.title('Individual traces, Runs:%s, NumBins:%s' %(runNums,Nbins))
	plt.plot(binCenters, I0BinOn)
	plt.show()

	#plt.figure()
	#plt.plot(binCenters, SigBinOn)
	#plt.title('Just SigBinOn')
	#plt.plot(binCenters, I0BinOn)
	#plt.show(block=True)

	plt.figure()
	plt.plot(binCenters, SigBinOn/I0BinOn)
	plt.title('Sig/I0, Runs:%s, NumBins:%s' %(runNums,Nbins))

	plt.figure()
	plt.plot(binCenters, SigBinOn)
	plt.title('Normalized, Runs:%s, NumBins:%s' %(runNums,Nbins))
	plt.show(block=True)
		

if Mode == 4 or Mode == 5 or Mode == 10: 
	plt.figure()	
	plt.subplot(211)
	xfl = np.append(binCenters[0:8],binCenters[18:-1])
	yfl = np.append(SigBinOff[0:8],SigBinOff[18:-1])
	flback = np.polyfit(xfl,yfl,3)
	flfit = np.poly1d(flback)
	x_new = np.linspace(xfl[0],xfl[-1],num=len(xfl)*100)
	y_bg_subtract = (SigBinOff-flfit(binCenters))

	def lorentzian(x,p):
		numerator = (p[0]**2)
		denominator = (x-(p[1]))**2+p[0]**2
		y = p[2]*(numerator/denominator)
		return y

	def residuals(p,y,x):
		err = y-lorentzian(x,p)
		return err

	p = [4,45,.0025]
	pbest = leastsq(residuals,p,args=(y_bg_subtract,binCenters),full_output=1)
	best_parameters = pbest[0]
	fit_lor = lorentzian(x_new,best_parameters)

	def FWHM(x,y):
		half_max = max(y)/2.
		d = np.sign(half_max-np.array(y[0:-1])) - np.sign(half_max - np.array(y[1:]))
		left_idx = str.find(d>0)[0]
		right_idx = str.find(d<0)[-1]
		return x[right_idx] - x[left_idx]
	
	plt.plot(binCenters,SigBinOn,'b.-', label='Laser On')
	plt.plot(binCenters,SigBinOff,'r.-', label= 'Laser off')
        #plt.errorbar(binCenters, SigBinOff, yerr=OffError, fmt='o-')
	plt.plot(x_new,flfit(x_new)+fit_lor,'g-')
	plt.title('Theta Scan Runs:%s' %(runNums))
	plt.xlabel('Theta (deg)')
	#plt.xlim([30,60])
	plt.ylabel(r'$\Delta$I/I$_0$')
	#legend = plt.legend(loc='upper right',shadow=True)	
	plt.grid()
	plt.show()

	#plt.figure()
	plt.subplot(212)
	plt.plot(binCenters,y_bg_subtract/flfit(binCenters),'ro')
	plt.plot(x_new,fit_lor/flfit(x_new),'k-',label= 'width = %.2f deg' %(abs(pbest[0][0]*2)))
	plt.xlabel('Theta (deg)')
	#plt.xlim([30,60])
	plt.ylabel(r'$\Delta$I/I$_0$')
	legend = plt.legend(loc='upper right',shadow=True)

	plt.grid()
	plt.show(block=True)

	
	#fig, ax = plt.subplots()
	#ax.plot(t, s)
	#ax.grid(True)

if Mode == 9: 
	plt.figure()
	plt.plot(binCenters, SigBinOn)
	plt.title('Individual traces, Runs:%s, NumBins:%s' %(runNums,Nbins))
	plt.plot(binCenters, I0BinOn)
	plt.show(block=True)

	#plt.figure()
	#plt.plot(binCenters, SigBinOn)
	#plt.title('Just SigBinOn')
	#plt.plot(binCenters, I0BinOn)
	#plt.show(block=True)

	plt.figure()
	plt.plot(binCenters, SigBinOn/I0BinOn)
	plt.title('Sig/I0, Runs:%s, NumBins:%s' %(runNums,Nbins))

	plt.figure()
	plt.plot(binCenters, SigBinOn)
	plt.title('Normalized, Runs:%s, NumBins:%s' %(runNums,Nbins))

#Save Output to file
if save==1: 
	runstring = str(runNums)
	np.savez('./PostAnalysis/' + 'Runs'+runstring +'_smd2.npz', SigBinOff = SigBinOff, binCenters=binCenters)
	DATA = np.load('./PostAnalysis/' + 'Runs'+runstring +'_smd2.npz') #Reload npz to save again as .mat, meh...
	io.savemat('./PostAnalysis/'+ 'Runs'+runstring+'_smd2.mat', DATA)

if 2 == 4: 
	runstring = str(runNums)
	np.savez('./PostAnalysis/' + 'Mode1'+ 'Runs'+runstring+'Bins'+ str(Nbins) +'_smd2.npz', Sig=SigBinOn/I0BinOn, bins=binCenters)
	DATA = np.load('./PostAnalysis/' +'Mode1'+ 'Runs'+runstring+'Bins'+ str(Nbins) +'_smd2.npz') #Reload npz to save again as .mat, meh...
	io.savemat('./PostAnalysis/'+ 'Mode1'+ 'Runs'+runstring+'Bins'+ str(Nbins) +'_smd2.mat', DATA) # Saving matlab format

if 2 == 5: 
	runstring = str(runNums)
	np.savez('./PostAnalysis/' + 'Mode5'+ 'Runs'+runstring+'Bins'+ str(Nbins) + det+'_smd2.npz', Sig=SigBinOn/I0BinOn, Sigoff=SigBinOff/I0BinOff, bins=binCenters, OnError=OnError, OffError=OffError)
	DATA = np.load('./PostAnalysis/' +'Mode5'+ 'Runs'+runstring+'Bins'+ str(Nbins) +det +'_smd2.npz') #Reload npz to save again as .mat, meh...
	io.savemat('./PostAnalysis/'+ 'Mode5'+ 'Runs'+runstring+'Bins'+ str(Nbins) +det +'_smd2.mat', DATA) # Saving matlab format

if 1==0:
	data15 = np.load('./PostAnalysis/Runs[15]_smd2.npz')
	data17 = np.load('./PostAnalysis/Runs[17]_smd2.npz')
	data18 = np.load('./PostAnalysis/Runs[18]_smd2.npz')
	data2021 = np.load('./PostAnalysis/Runs'+str([20,21])+'_smd2.npz')
	data23 = np.load('./PostAnalysis/Runs[23]_smd2.npz')
	data24 = np.load('./PostAnalysis/Runs[24]_smd2.npz')
	data25 = np.load('./PostAnalysis/Runs[25]_smd2.npz')
	data262728 = np.load('./PostAnalysis/Runs'+str([26,27,28])+'_smd2.npz')
	data2930 = np.load('./PostAnalysis/Runs'+str([29,30])+'_smd2.npz')
	data31 = np.load('./PostAnalysis/Runs'+str([31])+'_smd2.npz')
	data3132 = np.load('./PostAnalysis/Runs'+str([31,32])+'_smd2.npz')
	data313233 = np.load('./PostAnalysis/Runs'+str([31,32,33])+'_smd2.npz')
	data3536 = np.load('./PostAnalysis/Runs'+str([35,36])+'_smd2.npz')
	data3839 = np.load('./PostAnalysis/Runs'+str([38,39])+'_smd2.npz')
	data32 = np.load('./PostAnalysis/Runs'+str([32])+'_smd2.npz')
	data33 = np.load('./PostAnalysis/Runs'+str([33])+'_smd2.npz')
	data34 = np.load('./PostAnalysis/Runs'+str([34])+'_smd2.npz')
	data35 = np.load('./PostAnalysis/Runs'+str([35])+'_smd2.npz')
	data36 = np.load('./PostAnalysis/Runs'+str([36])+'_smd2.npz')
	data4041 = np.load('./PostAnalysis/Runs'+str([40,41])+'_smd2.npz')
	data4344 = np.load('./PostAnalysis/Runs'+str([43,44])+'_smd2.npz')
	data454647 = np.load('./PostAnalysis/Runs'+str([45,46,47])+'_smd2.npz')
	data4849 = np.load('./PostAnalysis/Runs'+str([48,49])+'_smd2.npz')
	data49 = np.load('./PostAnalysis/Runs'+str([49])+'_smd2.npz')
	data505152 = np.load('./PostAnalysis/Runs'+str([50,51,52])+'_smd2.npz')
	data56 = np.load('./PostAnalysis/Runs'+str([56])+'_smd2.npz')
	data5758 = np.load('./PostAnalysis/Runs'+str([57,58])+'_smd2.npz')
	data59 = np.load('./PostAnalysis/Runs'+str([59])+'_smd2.npz')
	data6061 = np.load('./PostAnalysis/Runs'+str([60,61])+'_smd2.npz')

if 1==0:
	plt.figure()
	#plt.plot(data15['binCenters'],data15['SigBinOff'],'g-',label='65K, 50fs')
	plt.plot(data17['binCenters'],1.1*data17['SigBinOff'],'r-',label='65K, 200fs')
	plt.plot(data18['binCenters'],1.05*data18['SigBinOff'],'b-',label='65K, 400fs')
	plt.plot(data2021['binCenters'],1.02*data2021['SigBinOff'],'k-',label='110K, 400fs')
	plt.plot(data23['binCenters'],data23['SigBinOff'],'m-',label='150K, 400fs')
	plt.plot(data24['binCenters'],data24['SigBinOff'],'y-',label='200K, 400fs')
	plt.plot(data25['binCenters'],data25['SigBinOff'],'c-',label='250K, 400fs')
	plt.plot(data2628['binCenters'],data2628['SigBinOff'],'g--',label='65K, 500fs')
	plt.plot(data2930['binCenters'],1.05*data2930['SigBinOff'],'r--',label='65K, 50fs')
	plt.ylim([65,115])
	plt.xlim([30,60])
	plt.grid()
	plt.xlabel('Sample theta (deg)')
	plt.ylabel(r'$\Delta$I/I$_0$')
	legend = plt.legend(loc='lower right',shadow=True)

if 1==0:
	plt.figure()
	#plt.plot(data262728['binCenters'],data262728['SigBinOff'],'g--',label='65K, 500fs')
	#plt.plot(data31['binCenters'],.93*data31['SigBinOff'],'r-',label='65K, 10fs first')
	#plt.plot(data32['binCenters'],.93*data32['SigBinOff'],'g-',label='65K, 10fs second')
	#plt.plot(data33['binCenters'],.93*data33['SigBinOff'],'b-',label='65K, 10fs third')
	#plt.plot(data34['binCenters'],.93*data34['SigBinOff'],'k-',label='65K, 10fs fourth')
	plt.plot(data3536['binCenters'],.95*data3536['SigBinOff'],'c-',label='65K, 15fs')
	plt.plot(data3839['binCenters'],.93*data3839['SigBinOff'],'m-',label='80K, 15fs')
	plt.plot(data4041['binCenters'],.93*data4041['SigBinOff'],'g-',label='110K, 15fs')
	plt.plot(data4344['binCenters'],.85*data4344['SigBinOff'],'r-',label='130K, 15fs')
	plt.plot(data454647['binCenters'],.85*data454647['SigBinOff'],'k-',label='150K, 15fs')
	plt.plot(data4849['binCenters'],0.85*data4849['SigBinOff'],'b-',label='200K, 15fs')
	plt.plot(data505152['binCenters'],0.85*data505152['SigBinOff'],'y-',label='250K, 15fs')
	plt.grid()
	plt.ylim([60,110])
	plt.xlim([30,60])
	plt.xlabel('Sample theta (deg)')
	plt.ylabel(r'$\Delta$I/I$_0$')
	legend = plt.legend(loc='lower right',shadow=True)

if 1==0:
	plt.figure()
	plt.plot(data2021['binCenters'],1.02*data2021['SigBinOff'],'k-',label='110K, 400fs (early in shift)')
	#plt.plot(data4041['binCenters'],.95*data4041['SigBinOff'],'g-',label='110K, 15fs (middle of shift)')
	plt.plot(data56['binCenters'],.93*data56['SigBinOff'],'b-',label='110K, 15fs (late in shift)')
	plt.plot(data5758['binCenters'],.93*data5758['SigBinOff'],'r-',label='110K, 50fs (late in shift)')
	plt.plot(data59['binCenters'],.88*data59['SigBinOff'],'c-',label='110K, 200fs (late in shift)')
	plt.plot(data6061['binCenters'],.93*data6061['SigBinOff'],'m-',label='110K, 1000fs (late in shift)')
	plt.ylabel(r'$\Delta$I/I$_0$')
	plt.xlabel('Sample theta (deg)')
	plt.xlim([30,60])
	legend = plt.legend(loc='lower right',shadow=True)
	plt.show()

if 1==0:
	plt.figure()
	plt.plot(data2021['binCenters'],1.02*data2021['SigBinOff'],'k-',label='110K, 400fs (early in shift)')
	plt.plot(data4041['binCenters'],.95*data4041['SigBinOff'],'g-',label='110K, 15fs (middle of shift)')
	plt.ylabel(r'$\Delta$I/I$_0$')
	plt.xlabel('Sample theta (deg)')
	plt.xlim([30,60])
	legend = plt.legend(loc='lower right',shadow=True)
	plt.show()


