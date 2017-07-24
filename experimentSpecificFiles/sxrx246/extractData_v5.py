
#Versions
#Beta: Matt's orginal script for his experiment
#V1: first iteration of data extraction for sxrl0916
# 	What was changed: 
#V2: Adjusted for "damage" return of encoders (Both mono and delay stage), Will set as NaN for damage case
#V3: Added Epics PV for Encoder, and CH_0 for Delay stage (DAQ side)
#v4: Had to add Old extraction for Laser Diode, Not sure why it was giving me issues
#v5: Added PhaseCavity, Energy calc from mono, and waveplate
#V6: Add All possible Detectors
import psana
from psana import *
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as io
from scipy.fftpack import fft, fftshift, ifft, ifftshift, rfft, irfft, fftfreq

lower_freq = 0
upper_freq = 15
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
assert size>1, 'At least 2 MPI ranks required'

import argparse
import ConfigParser
parser = argparse.ArgumentParser()
parser.add_argument("-c","--cfg", help="config file")
parser.add_argument('-r','--run', help='run number from DAQ')
parser.add_argument('-n','--noe', help='number of events, all events=-1', default=-1, type=int)

args = parser.parse_args()

# parse config file
config = ConfigParser.ConfigParser()
config.read(args.cfg)
pars = {}
pars['expName'] = config.get('Main','expName')
#MCPI0
pars['I0_AcqBoard'] = config.getint('MCPI0','I0_AcqBoard')
pars['I0_AcqChan'] = config.getint('MCPI0','I0_AcqChan')
pars['I0_windowMin'] = config.getint('MCPI0','I0_windowMin')
pars['I0_windowMax'] = config.getint('MCPI0','I0_windowMax')
pars['I0_width'] = config.getint('MCPI0','I0_width')

#MCP
pars['MCP_AcqBoard']=config.getint('MCP','MCP_AcqBoard')
pars['MCP_AcqChan']=config.getint('MCP','MCP_AcqChan')
pars['MCP_windowMin']=config.getint('MCP','Mcp_windowMin')
pars['MCP_windowMax']=config.getint('MCP','MCP_windowMax')
pars['MCP_width']=config.getint('MCP','MCP_width')

# APD NO AP
pars['APD_NOAP_AcqBoard']=config.getint('APD NO AP','APD_NOAP_AcqBoard')
pars['APD_NOAP_AcqChan']=config.getint('APD NO AP','APD_NOAP_AcqChan')
pars['APD_NOAP_windowMin']=config.getint('APD NO AP','APD_NOAP_windowMin')
pars['APD_NOAP_windowMax']=config.getint('APD NO AP','APD_NOAP_windowMax')
pars['APD_NOAP_width']=config.getint('APD NO AP','APD_NOAP_width')

#APD AP
pars['APD_AP_AcqBoard']=config.getint('APD AP','APD_AP_AcqBoard')
pars['APD_AP_AcqChan']=config.getint('APD AP','APD_AP_AcqChan')
pars['APD_AP_windowMin']=config.getint('APD AP','APD_AP_windowMin')
pars['APD_AP_windowMax']=config.getint('APD AP','APD_AP_windowMax')
pars['APD_AP_width']=config.getint('APD AP','APD_AP_width')

#Laser Diode
pars['Diode_AcqBoard']= config.getint('Laser Diode','Diode_AcqBoard')
pars['Diode_AcqChan'] = config.getint('Laser Diode','Diode_AcqChan')
pars['Diode_Thres'] = config.getfloat('Laser Diode','Diode_Thres')

#MCT1
pars['MCT1_AcqBoard']=config.getint('MCT1','MCT1_AcqBoard')
pars['MCT1_AcqChan']=config.getint('MCT1','MCT1_AcqChan')
pars['MCT1_windowMin']=config.getint('MCT1','MCT1_windowMin')
pars['MCT1_windowMax']=config.getint('MCT1','MCT1_windowMax')
pars['MCT1_width']=config.getint('MCT1','MCT1_width')

#MCT2
pars['MCT2_AcqBoard']=config.getint('MCT2','MCT2_AcqBoard')
pars['MCT2_AcqChan']=config.getint('MCT2','MCT2_AcqChan')
pars['MCT2_windowMin']=config.getint('MCT2','MCT2_windowMin')
pars['MCT2_windowMax']=config.getint('MCT2','MCT2_windowMax')
pars['MCT2_width']=config.getint('MCT2','MCT2_width')

#pars['']=config.getint('','')

#EVT Codes
pars['laserOn'] = config.getint('EventCodes','laserOn')
pars['laserOff'] = config.getint('EventCodes','laserOff')
pars['BYKIK'] = config.getint('EventCodes','BYKIK')
pars['lowRate'] = config.getint('EventCodes','lowRate')
pars['highRate'] = config.getint('EventCodes','highRate')

## main section
expName = pars['expName']
runNum = args.run
#runString = 'exp=SXR/sxrl0916:run='+'runNum'
runString = 'exp=SXR/'+expName+':run='+runNum+':smd'
#runString += ':dir=/reg/d/ffb/sxr/'+expName+'/xtc:live'

#if runNum == 80:
#	DiodeOnInd = 1628
#	DiodeOffInd = 1731
#	DiodeBoard = 1
#	DiodeChan = 2
#	MCPind = 3200
#	APDNOAPind = 3197
#	APDAPind = 3224
#elif runNum == 87:
#	DiodeOnInd = 1628
#	DiodeOffInd = 1731
#	DiodeBoard = 1
#	DiodeChan = 2
#	MCPind = 3200
#	APDNOAPind = 3198
#	APDAPind = 3223
#elif runNum == 88:
#	DiodeOnInd = 1628
#	DiodeOffInd = 1731
#	DiodeBoard = 1
#	DiodeChan = 2
#	MCPind = 3199
#	APDNOAPind = 3197
#	APDAPind = 3223
#elif runNum == 91:
#	DiodeOnInd = 1628
#	DiodeOffInd = 1731
#	DiodeBoard = 1
#	DiodeChan = 2
#	MCPind = 3199
#	APDNOAPind = 3197
#	APDAPind = 3225
#elif runNum == 132:
#	DiodeOnInd = 1241
#	DiodeOffInd = 1246
#	DiodeBoard = 2
#	DiodeChan = 1
#	MCPind = 1205
#	APDNOAPind = 1202
#	APDAPind = 1216
#elif runNum == 133:
#	DiodeOnInd = 1241
#	DiodeOffInd = 1246
#	DiodeBoard = 2
#	DiodeChan = 1
#	MCPind = 1205
#	APDNOAPind = 1202
#	APDAPind = 1216
#elif runNum == 134:
#	DiodeOnInd = 1241
#	DiodeOffInd = 1246
#	DiodeBoard = 2
#	DiodeChan = 1
#	MCPind = 1205
#	APDNOAPind = 1202
#	APDAPind = 1216
#else:
#	DiodeOnInd = 1241
#	DiodeOffInd = 1246
#	DiodeBoard = 2
#	DiodeChan = 1
#	MCPind = 1205
#	APDNOAPind = 1202
#	APDAPind = 1216
	

ds = DataSource(runString)
#acq1src = psana.Source('DetInfo(SxrEndstation.0:Acqiris.1)')
#acq2src = psana.Source('DetInfo(SxrEndstation.0:Acqiris.2)')

# I0 detector
#I0Det = pars['I0']

# GMD I0
GMD = Detector('GMD')

# Acqiris waveform detector (board number)
acq1src = Detector('Acq01')
acq2src = Detector('Acq02')

#delay stage encoder
DlsEnc = Detector('DLS_encoder') #verify this detector name

# evr
evr = Detector('evr0')

# epics PV's
epics = ds.env().epicsStore()

# event codes
BYKIK = pars['BYKIK']
laserOn = pars['laserOn']
laserOff = pars['laserOff']
lowRate = pars['lowRate']
highRate = pars['highRate']

# scale and offset to convert encoder counts to match RBV's (for grating)
#scale = -51696.8
#offset = -5.378

# signal parameters
#sigChan = pars['Sig_AcqChan']
#sigMin = pars['Sig_windowMin']
#sigMax = pars['Sig_windowMax']
#sigWidth = pars['Sig_width']

# MCPI0 parameters
MCPI0Board = pars['I0_AcqBoard']
MCPI0Chan = pars['I0_AcqChan']
MCPI0Min = pars['I0_windowMin']
MCPI0Max = pars['I0_windowMax']
MCPI0Width = pars['I0_width']

#MCP parameters
MCPBoard = pars['MCP_AcqBoard']
MCPChan = pars['MCP_AcqChan']
MCPMin = pars['MCP_windowMin']
MCPMax = pars['MCP_windowMax']
MCPWidth = pars['MCP_width']

#APD NO AP
APDNOAPBoard = pars['APD_NOAP_AcqBoard']
APDNOAPChan = pars['APD_NOAP_AcqChan']
APDNOAPMin = pars['APD_NOAP_windowMin']
APDNOAPMax = pars['APD_NOAP_windowMax']
APDNOAPWidth = pars['APD_NOAP_width']

#APD AP
APDAPBoard = pars['APD_AP_AcqBoard']
APDAPChan = pars['APD_AP_AcqChan']
APDAPMin = pars['APD_AP_windowMin']
APDAPMax = pars['APD_AP_windowMax']
APDAPWidth = pars['APD_AP_width']

#Laser Diode
DiodeBoard = pars['Diode_AcqBoard']
DiodeChan = pars['Diode_AcqChan']
Diode_Thres = pars['Diode_Thres']

#MCT1
MCT1Board = pars['MCT1_AcqBoard']
MCT1Chan = pars['MCT1_AcqChan']
MCT1Min = pars['MCT1_windowMin']
MCT1Max = pars['MCT1_windowMax']
MCT1Width = pars['MCT1_width']

#MCT2
MCT2Board = pars['MCT2_AcqBoard']
MCT2Chan = pars['MCT2_AcqChan']
MCT2Min = pars['MCT2_windowMin']
MCT2Max = pars['MCT2_windowMax']
MCT2Width = pars['MCT2_width']


# initialize arrays

#Acq Traces 
MCPI0 = np.empty(0)
DiodeOn = np.empty(0)
DiodeOff = np.empty(0)
DiodeBack = np.empty(0)
MCP = np.empty(0)
APDNOAP = np.empty(0)
#APDNOAPappend = np.zeros(500)
#APDNOAPappend = np.append([APDNOAPappend],[APDNOAPappend], axis=0)
APDAP = np.empty(0)
LaserDiode = np.empty(0) #Actual diode measuring laser presence
DiodeTrace = np.empty(0)
MCT1 = np.empty(0)
MCT2 = np.empty(0)

#background arrays:
MCPI0Back = np.empty(0)
MCPBack =np.empty(0)
APDNOAPBack = np.empty(0)
APDAPBack = np.empty(0)
MCT1Back = np.empty(0)
MCT2Back = np.empty(0)

#Instruments, Epics
GMDI0 = np.empty(0)
eventNum = np.empty(0)
laserOnEvt = np.empty(0)
lowRateEvt = np.empty(0)
highRateEvt = np.empty(0)
delay = np.empty(0)
gratingEnc = np.empty(0)
gratingEpics = np.empty(0)
laserMoving = np.empty(0)
bykikEvt = np.empty(0)
laserOffEvt = np.empty(0)
DelayEnc = np.empty(0) # [nm/count]
DelayEpics = np.empty(0) #cross reference to delayEnc [mm]
PhaseCavity_t1 = np.empty(0)
PhaseCavity_t2 = np.empty(0)
mirrorEpics = np.empty(0)


#Orientation Arrays
Sample_Theta= np.empty(0)
Sample_Flip= np.empty(0)
Detector_2theta= np.empty(0)
Detector_Flip= np.empty(0)
attenuation = np.empty(0)

#Calculated Arrays
energy = np.empty(0)
waveplate = np.empty(0)

for nevent, evt in enumerate(ds.events()):
	

	if nevent == args.noe: break
	if nevent%(size)!=rank: continue
		
        #if not hasattr(acqsrc,'waveform'): continue
	if acq1src.waveform(evt) is None:          #CHANGED FOR ACQ01 DOWN
		continue

        if acq2src.waveform(evt) is None:
                continue

	######  GMD ##########
	gmdEvt = GMD.get(evt)
	# check for damage
	if gmdEvt is None:
		GMDI0 = np.append(GMDI0, np.nan)
	else:
		GMDI0 = np.append(GMDI0, gmdEvt.milliJoulesPerPulse())

	####### MONO ########
        # read mono encoders
        #mono = monoEnc.get(evt)
        mono = evt.get(UsdUsb.FexDataV1,Source('MONO_encoder'))
	# get mono position
        if mono is None: 
		gratingEnc = np.append(gratingEnc, np.nan)
		gratingEpics = np.append(gratingEpics, epics.value('SXR:MON:MMS:06.RBV'))
	else:
		gratingEnc = np.append(gratingEnc, mono.encoder_values()[1])
		gratingEpics = np.append(gratingEpics, epics.value('SXR:MON:MMS:06.RBV'))
	
	waveplate = np.append(waveplate,epics.value('SXR:LAS:MCN1:04.RBV'))
	mirrorEpics = np.append(mirrorEpics, epics.value('SXR:MON:MMS:05.RBV'))
	attenuation = np.append(attenuation, epics.value('GATT:FEE1:310:R_ACT'))
	
	
	#####  get event codes #######
       	eventCodes = evr.eventCodes(evt)
	if eventCodes is None:
		bykikEvt = np.append(bykikEvt, 0)
		laserOnEvt = np.append(laserOnEvt, 0)
		laserOffEvt = np.append(laserOffEvt, 0)
		lowRateEvt = np.append(lowRateEvt,0)
		highRateEvt = np.append(highRateEvt,0)
	else:
		# check for x-ray off
       		if BYKIK in eventCodes: 
			bykikEvt =  np.append(bykikEvt,1)
		else: 
			bykikEvt = np.append(bykikEvt,0)
		if laserOn in eventCodes: 
			laserOnEvt = np.append(laserOnEvt,1)
		else: 
			laserOnEvt = np.append(laserOnEvt,0)
		if laserOff in eventCodes:
			laserOffEvt = np.append(laserOffEvt,1)
		else:
			laserOffEvt = np.append(laserOffEvt,0)
		if lowRate in eventCodes:
			lowRateEvt = np.append(lowRateEvt,1)
		else:
			lowRateEvt = np.append(lowRateEvt,0)
		if highRate in eventCodes:
			highRateEvt = np.append(highRateEvt,1)
		else:
			highRateEvt = np.append(highRateEvt,0)

	####### Phase Cavity ############
	PCevt = evt.get(psana.Bld.BldDataPhaseCavity,psana.Source("BldInfo(PhaseCavity)"))
	if PCevt is None:
		PhaseCavity_t1 = np.append(PhaseCavity_t1, np.nan)
		PhaseCavity_t2 = np.append(PhaseCavity_t2, np.nan)
	else: 
	        PhaseCavity_t1 = np.append(PhaseCavity_t1, PCevt.fitTime1())
                PhaseCavity_t2 = np.append(PhaseCavity_t2, PCevt.fitTime2())


	####### Orientations ########### 
	if epics is None:
		Sample_Theta = np.append(Sample_Theta, np.nan)
		Sample_Flip = np.append(Sample_Flip, np.nan)
		Detector_2theta = np.append(Detector_2theta, np.nan)
		Detector_Flip = np.append(Detector_Flip, np.nan)
	else:
		Sample_Theta = np.append(Sample_Theta, epics.value('SXR:EXP:MMS:10.RBV'))
		Sample_Flip = np.append(Sample_Flip, epics.value('SXR:EXP:MMS:12.RBV')) #switched to channel 12 for sample_azimuth (sample_flip is channel 11)
		Detector_2theta = np.append(Detector_2theta, epics.value('SXR:EXP:MMS:13.RBV'))
		Detector_Flip = np.append(Detector_Flip, epics.value('SXR:EXP:MMS:14.RBV'))
	
	########  Delay Stage ###########
	#Dls_Tmp = DlsEnc.get(evt)
	Dls_Tmp = evt.get(UsdUsb.FexDataV1,Source('DLS_encoder'))
	#Get Delay Stage Encoder
	if Dls_Tmp is None:
		DelayEnc = np.append(DelayEnc, np.nan) #Not Sure this [Num]
		DelayEpics = np.append(DelayEpics, np.nan)
	else:
		DelayEnc = np.append(DelayEnc, Dls_Tmp.encoder_values()[0]) #CH_0 
		DelayEpics = np.append(DelayEpics, epics.value('SXR:LAS:MCN1:06.RBV')) 

	########## Laser Diode ############# 
	#raw = evt.get(psana.Acqiris.DataDescV1, src)
        #g = raw.data(2)
        #g0 = g.waveforms()[0]
	#DiodeLogical = np.amax(g0)>15000
	#LaserDiode = np.append(LaserDiode,DiodeLogical)
	#Laser Diode
	if DiodeBoard == 1:
		DiodeTrace = acq1src.waveform(evt)[DiodeChan].flatten()
	else:
		DiodeTrace = acq2src.waveform(evt)[DiodeChan].flatten()

	DiodeOnInd = 1241#1628#
	DiodeOffInd = 1446#1731#
	DiodeWidth = 1
	DiodeBackNum = np.mean(DiodeTrace[500-DiodeWidth:500+DiodeWidth])
	DiodeOnNum = np.mean(DiodeTrace[DiodeOnInd-DiodeWidth:DiodeOnInd+DiodeWidth])
	DiodeOffNum = np.mean(DiodeTrace[DiodeOffInd-DiodeWidth:DiodeOffInd:DiodeWidth])
	DiodeBack = np.append(DiodeBack,DiodeBackNum)
	DiodeOn = np.append(DiodeOn,DiodeOnNum)
	DiodeOff = np.append(DiodeOff,DiodeOffNum)

	#Thres to logical mask
	DiodeLogical = np.amax(DiodeTrace)>Diode_Thres 
	LaserDiode = np.append(LaserDiode, DiodeLogical)


	###### MCPI0 ########
	if MCPI0Board == 1:
		MCPI0_1 = -acq1src.waveform(evt)[MCPI0Chan].flatten()
       	else:
		MCPI0_1 = -acq2src.waveform(evt)[MCPI0Chan].flatten()

	MCPI0Back = np.mean(MCPI0_1[0:1000])
       	#MCPI0_1 = MCPI0_1[MCPI0Min:MCPI0Max]
	MCPind = 1204 #3199 #np.argmax(MCPI0_1)
       	MCPI0Num = np.mean(MCPI0_1[MCPind-MCPI0Width:MCPind+MCPI0Width]) #What is this line?
	MCPI0 = np.append(MCPI0,MCPI0Num-MCPI0Back)
	#MCPI0 = np.append(MCPI0,MCPI0Num-MCPI0Back)

	#####  MCP signal ########
	if MCPBoard == 1:
       		MCP1 = -acq1src.waveform(evt)[MCPChan].flatten()
	else: 
		MCP1 = -acq2src.waveform(evt)[MCPChan].flatten() 
       	# find and subtract background
       	MCPBack = np.mean(MCP1[0:MCPMin-100])
	#MCP1 = MCP1[MCPMin:MCPMax]       	
	# find peak
	#MCPind = np.argmax(MCP1)
	#MCPind = 3190#1205  #3190       	
	MCPNum = np.mean(MCP1[MCPind-MCPWidth:MCPind+MCPWidth])
	#Sig = np.append(Sig, SigNum-SigBack)
	MCP = np.append(MCP,MCPNum-MCPBack) #No point in adding more noise
	eventNum = np.append(eventNum, nevent)
	
        #####  APDNOAP signal ########
        if APDNOAPBoard == 1:
                APDNOAP1 = -acq1src.waveform(evt)[APDNOAPChan].flatten()
        else:
                APDNOAP1 = -acq2src.waveform(evt)[APDNOAPChan].flatten()
        # find and subtract background
	#APDNOAPwin = np.array(APDNOAP1[1000:1500])
	#APDNOAPappend = np.append(APDNOAPappend,[APDNOAPwin], axis=0)
        APDNOAPBack = np.mean(APDNOAP1[0:1000])
        #APDNOAP1 = APDNOAP1[APDNOAPMin:APDNOAPMax]
        # find peak
        #APDNOAPind = np.argmax(APDNOAP1)
	APDNOAPind = 1201#3197#

	#fft filter

	Fs = 120
	dt = 1/Fs
	N = len(APDNOAP1)
	dF = Fs/N
	f = np.linspace(-Fs/2,Fs/2,N)
	BPF = np.logical_and(abs(f) > lower_freq, abs(f) < upper_freq)
	BPF = BPF.astype(int)
	signal = APDNOAP1 - APDNOAPBack
	spectrum = np.fft.fftshift(fft(signal))
	spectrum = BPF * spectrum
	signal = ifft(np.fft.ifftshift(spectrum))

        APDNOAPNum = np.mean(signal[APDNOAPind-APDNOAPWidth:APDNOAPind+APDNOAPWidth])
	#APDNOAPNum = APDNOAP1[APDNOAPind]-APDNOAPBack
        #Sig = np.append(Sig, SigNum-SigBack)
        APDNOAP = np.append(APDNOAP,APDNOAPNum) #No point in adding more noise
	
        #####  APDAP signal ########
	if APDAPBoard == 1:
                APDAP1 = -acq1src.waveform(evt)[APDAPChan].flatten()
        else:
                APDAP1 = -acq2src.waveform(evt)[APDAPChan].flatten()
        # find and subtract background
        APDAPBack = np.mean(APDAP1[0:1000])
        #APDAP1 = APDAP1[APDAPMin:APDAPMax]
        # find peak
        #APDAPind = np.argmax(APDAP1)
	APDAPind = 1216#3224#


	N = len(APDAP1)
	dF = Fs/N
	f = np.linspace(-Fs/2,Fs/2,N)
	BPF = np.logical_and(abs(f) > lower_freq, abs(f) < upper_freq)
	BPF = BPF.astype(int)
	signal = APDAP1 - APDAPBack
	spectrum = np.fft.fftshift(fft(signal))
	spectrum = BPF * spectrum
	signal = ifft(np.fft.ifftshift(spectrum))
       
	APDAPNum = np.mean(signal[APDAPind-APDAPWidth:APDAPind+APDAPWidth])
        #Sig = np.append(Sig, SigNum-SigBack)
        APDAP = np.append(APDAP,APDAPNum) #No point in adding more noise


        #####  MCT1 signal ########
        if MCT1Board == 1:
                MCT11 = -acq1src.waveform(evt)[MCT1Chan].flatten()
        else:
                MCT11 = -acq2src.waveform(evt)[MCT1Chan].flatten()
        # find and subtract background
        MCT1Back = np.mean(MCT11[0:MCT1Min-100])
        MCT11 = MCT11[MCT1Min:MCT1Max]
        # find peak
        MCT1ind = np.argmax(MCT11)
        #MCT1Num = np.mean(MCT11[MCT1ind-MCT1Width:MCT1ind+MCT1Width])
        MCT1Num = np.sum(MCT11[MCT1ind-MCT1Width:MCT1ind+MCT1Width])
	#Sig = np.append(Sig, SigNum-SigBack)
        MCT1 = np.append(MCT1,MCT1Num) #No point in adding more noise

	        #####  MCT2 signal ########
        if MCT2Board == 1:
                MCT21 = -acq1src.waveform(evt)[MCT2Chan].flatten()
        else:
                MCT21 = -acq2src.waveform(evt)[MCT2Chan].flatten()
        # find and subtract background
        MCT2Back = np.mean(MCT21[0:MCT2Min-100])
        MCT21 = MCT21[MCT2Min:MCT2Max]
        # find peak
        MCT2ind = np.argmax(MCT21)
        MCT2Num = np.mean(MCT21[MCT2ind-MCT2Width:MCT2ind+MCT2Width])
        #Sig = np.append(Sig, SigNum-SigBack)
        MCT2 = np.append(MCT2,MCT2Num) #No point in adding more noise


	
	
	# electronic delay
	delay = np.append(delay, epics.value('LAS:FS2:VIT:FS_TGT_TIME_DIAL'))
	# check if laser timing is not set (0 if not set)
	if epics.value('LAS:FS2:MMS:PH.DMOV') is not None:
		laserMoving = np.append(laserMoving, epics.value('LAS:FS2:MMS:PH.DMOV'))


# gather data from all the nodes

#Sig = comm.gather(Sig)
MCPI0 = comm.gather(MCPI0)
MCPI0Back = comm.gather(MCPI0Back)
MCP = comm.gather(MCP)
MCPBack = comm.gather(MCPBack)
APDNOAP = comm.gather(APDNOAP)
#APDNOAPappend = comm.gather(APDNOAPappend)
APDNOAPBack = comm.gather(APDNOAPBack)
APDAP = comm.gather(APDAP)
APDAPBack = comm.gather(APDAPBack)
MCT1 = comm.gather(MCT1)
MCT1Back = comm.gather(MCT1Back)
MCT2 = comm.gather(MCT2)
MCT2Back = comm.gather(MCT2Back)



GMDI0 = comm.gather(GMDI0)
eventNum = comm.gather(eventNum)
laserOnEvt = comm.gather(laserOnEvt)
lowRateEvt = comm.gather(lowRateEvt)
highRateEvt = comm.gather(highRateEvt)
delay = comm.gather(delay)
gratingEnc = comm.gather(gratingEnc)
gratingEpics = comm.gather(gratingEpics)
laserMoving = comm.gather(laserMoving)
bykikEvt = comm.gather(bykikEvt)
laserOffEvt = comm.gather(laserOffEvt)
#SigBack = comm.gather(SigBack)
#I0Back = comm.gather(I0Back)

DelayEnc = comm.gather(DelayEnc)
DelayEpics = comm.gather(DelayEpics)
LaserDiode =comm.gather(LaserDiode)
DiodeOn = comm.gather(DiodeOn)
DiodeOff = comm.gather(DiodeOff)
DiodeBack = comm.gather(DiodeBack)
Sample_Theta= comm.gather(Sample_Theta)
Sample_Flip= comm.gather(Sample_Flip)
Detector_2theta= comm.gather(Detector_2theta)
Detector_Flip= comm.gather(Detector_Flip)
attenuation = comm.gather(attenuation)

PhaseCavity_t1 = comm.gather(PhaseCavity_t1)
PhaseCavity_t2 = comm.gather(PhaseCavity_t2)
waveplate = comm.gather(waveplate)

# concatenate everything into a row vector

if rank==0:
	totalEvts = args.noe

	#	Sig = np.hstack((Sig[:]))
	 #       SigBack = np.hstack((SigBack[:]))
	MCPI0 = np.hstack((MCPI0[:]))
        MCPI0Back = np.hstack((MCPI0Back[:]))
	MCP = np.hstack((MCP[:]))
        MCPBack = np.hstack((MCPBack[:]))
        APDNOAP = np.hstack((APDNOAP[:]))
	#APDNOAPappend = np.vstack((APDNOAPappend[:]))
        APDNOAPBack = np.hstack((APDNOAPBack[:]))
        APDAP = np.hstack((APDAP[:]))
        APDAPBack = np.hstack((APDAPBack[:]))
        MCT1 = np.hstack((MCT1[:]))
        MCT1Back = np.hstack((MCT1Back[:]))
        MCT2 = np.hstack((MCT2[:]))
        MCT2Back = np.hstack((MCT2Back[:]))
	
	#MCPI0 = np.hstack((MCPI0[:]))
        # = np.hstack((I0Back[:]))

	GMDI0 = np.hstack((GMDI0[:]))
	eventNum = np.hstack((eventNum[:]))
	laserOnEvt = np.hstack((laserOnEvt[:]))
	delay = np.hstack((delay[:]))
	gratingEnc = np.hstack((gratingEnc[:]))
	gratingEpics = np.hstack((gratingEpics[:]))
	laserMoving = np.hstack((laserMoving[:]))
	bykikEvt = np.hstack((bykikEvt[:]))
	laserOffEvt = np.hstack((laserOffEvt[:]))
	lowRateEvt = np.hstack((lowRateEvt[:]))
	highRateEvt = np.hstack((highRateEvt[:]))

	DelayEnc = np.hstack((DelayEnc[:]))
	DelayEpics = np.hstack((DelayEpics[:]))
	LaserDiode = np.hstack((LaserDiode[:]))
	DiodeOn = np.hstack((DiodeOn[:]))
	DiodeOff = np.hstack((DiodeOff[:]))
	DiodeBack = np.hstack((DiodeBack[:]))
	Sample_Theta= np.hstack((Sample_Theta[:]))
	Sample_Flip= np.hstack((Sample_Flip[:]))
	Detector_2theta= np.hstack((Detector_2theta[:]))
	Detector_Flip= np.hstack((Detector_Flip[:]))
	attenuation = np.hstack((attenuation[:]))

	PhaseCavity_t1 = np.hstack((PhaseCavity_t1[:]))
	PhaseCavity_t2 = np.hstack((PhaseCavity_t2[:]))

        gratingMin = np.amin(gratingEpics)
        gratingMax = np.amax(gratingEpics)
        encoderMin = np.amin(gratingEnc)
        encoderMax = np.amax(gratingEnc)
        waveplate = np.hstack((waveplate[:]))
	
        # scale encoders to epics values
        gratingEnc = gratingEnc - encoderMin
        gratingEnc = gratingEnc*(gratingMax-gratingMin)/(encoderMax-encoderMin)+ gratingMin

        # calculate photon energy based on encoder values
        mirrorAngle = mirrorEpics[0]/400 + .806008*np.pi/180
        gratingAngle = gratingEnc/400 + .00295*np.pi/180
        wavelength = 2*1e-5*np.sin(mirrorAngle)*np.sin(mirrorAngle-gratingAngle)*1e9
        energy = 1239.842/wavelength
	
	np.savez('./data/' + runNum + '_smd2.npz', MCPI0=MCPI0,MCP=MCP,APDNOAP=APDNOAP,APDAP=APDAP,MCT1=MCT1,MCT2=MCT2, GMDI0=GMDI0, eventNum=eventNum, laserOnEvt=laserOnEvt, delay=delay, gratingEnc=gratingEnc, gratingEpics=gratingEpics, laserMoving=laserMoving, bykikEvt=bykikEvt, laserOffEvt=laserOffEvt, lowRateEvt=lowRateEvt, highRateEvt=highRateEvt, attenuation=attenuation, DelayEnc=DelayEnc,DelayEpics=DelayEpics,LaserDiode=LaserDiode,DiodeOn=DiodeOn,DiodeOff=DiodeOff,DiodeBack=DiodeBack,Sample_Theta=Sample_Theta,Sample_Flip=Sample_Flip,Detector_2theta=Detector_2theta,Detector_Flip=Detector_Flip, PhaseCavity_t1 =PhaseCavity_t1, PhaseCavity_t2=PhaseCavity_t2, energy=energy, waveplate=waveplate)
	
	DATA = np.load('./data/' + runNum + '_smd2.npz') #Reload npz to save again as .mat, meh...
	io.savemat('./data/' + runNum + '_smd2.mat', DATA) # Saving matlab format

MPI.Finalize()

