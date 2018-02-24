import numpy as np
from pylab import *
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import time
import scipy as sci
import scipy.io as io
from scipy.optimize import leastsq
runNums=[6]#Make sure they're comma sepearated eg: [112,113]
Nbins = 31
save=0 #1 for save, 0 for no save

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
I0 = []
delay = []
laserOn = []
laserOff = []

Sample_Theta = []

MCPI0 = []
SmallAPD = []
LargeAPD = []

for run in runNums: 
	#Data File, .npz file
	data = h5py.File('sxrlq8415run'+str(run)+'.h5')
	# Pull data into Vectors
	Acq01 = data['Acq01']
	MCPI0 = array(Acq01['MCPI0'])	
	LargeAPD = array(Acq01['APDNOAP'])
	SmallAPD = array(Acq01['APDAP'])
	Sample_Theta = array(data['Sample_Theta'])
	EventCodes = data['evr']
	laserOn = array(EventCodes['code_76'])
	laserOff = array(EventCodes['code_77'])
	#laserOn = np.hstack((laserOn, data['laserOnEvt']))
	#laserOff = np.hstack((laserOff, data['laserOffEvt']))

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
	Sig = APDNOAP
	I0 = MCPI0
	Sample_Theta = Sample_Flip
	Mode = 5
if Mode == 8: 
	Sig = APDNOAP
	I0 = MCPI0
	Mode = 1
if Mode == 9 or Mode == 10:
	Sig = APDNOAP
	I0 = MCPI0

mask = np.logical_and(I0<100, I0>-5.001)

Sig = Sig[mask]
I0 = I0[mask]
Sample_Theta = Sample_Theta[mask]

#Normalize before binning
Sig = Sig/I0

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

# Sort data with respect to Delay, Theta, etc.
Sig = Sig[ind]
I0 = I0[ind]
Sample_Theta = Sample_Theta[ind]

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
	#delayMin = np.amin(gratingEpics)
	#delayMax = np.amax(gratingEpics)	
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	N = np.size(photon_energy)
	#N = np.size(gratingEpics)
if Mode == 4 or Mode == 5: 
	delayMin = np.amin(Sample_Theta)
	delayMax = np.amax(Sample_Theta)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	#binCenters = np.unique(Sample_Theta)
	#Nbins = len(binCenters)
	N = np.size(Sig)
if Mode == 9:
	delayMin = np.amin(waveplate)
	delayMax = np.amax(waveplate)
	binEdges = np.linspace(delayMin,delayMax,num=Nbins+1)
	binCenters = (binEdges[0:Nbins] + binEdges[1:Nbins+1])/2
	N = np.size(delay)
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
			SigBinOn[binNum] += Sig[i]
			I0BinOn[binNum] += I0[i]
			NormedOn[binNum] += Sig[i]/I0[i]
			counterOn[binNum] += 1

			SigOnSquared[binNum] += Sig[i]**2
			I0OnSquared[binNum] += I0[i]**2
			NormOnSquared[binNum] += (Sig[i]/I0[i])**2
			
		elif laserOn[i]==0:
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
	#fig, ax = plt.subplots()
	#plt.plot(binCenters, SigBinOn/I0BinOn, 'b^', binCenters, -SigBinOn/I0BinOn)#/I0BinOn)
	#plt.ylim([.23,.36])
	#ax.errorbar(binCenters, SigBinOn/I0BinOn, yerr=OnError, fmt='bo')
	#ax.errorbar(binCenters, SigBinOff/I0BinOff, yerr=OffError, fmt='g^')
	#plt.plot(binCenters, BK_APDAP, 'r^', binCenters, BK_APDAP)
	#plt.plot(binCenters, BK_APDNOAP, 'r^', binCenters, BK_APDNOAP)
	
	plt.subplot(211)
	xfl = np.append(binCenters[0:10],binCenters[22:-1])
	yfl = np.append(SigBinOff[0:10],SigBinOff[22:-1])
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
