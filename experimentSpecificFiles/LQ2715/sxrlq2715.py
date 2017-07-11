from psana import *
import sys
import datetime
import numpy as np

runnum = sys.argv[1]
if len(sys.argv) > 2:
	debug = True
else:
	debug = False

#Live data during beamtime
dsource = MPIDataSource('exp=sxrlq2715:run='+runnum+':smd:dir=/reg/d/ffb/sxr/sxrlq2715/xtc:live')
#After beamtime
#dsource = MPIDataSource('exp=sxrlq2715:run='+runnum+':smd')

detNames = DetNames()
epicsNames = DetNames('epics')

def myDetector(name, detlist = detNames, epics = epicsNames):
	""" Test if a detector is present in the run and return a tuple
		where first element is a boolean whether the detector is present or not
		and the second element is the detector object.
	"""
	for d in detlist:
		if name in d:
			return (True, Detector(name))

	for d in epics:
		if name in d:
			return (True, Detector(name))

	print('WARNING: No detector "' + name + '" in run ' + runnum) 
	return (False, Detector(name, accept_missing=True))

dlsDet = myDetector('DLS_encoder')
# The number of delay stage, in ps per encoder units
PS_PER_ENC = 1.33426e-4
# The approximate position of time zero, in encoder units
TIME_ZERO = -6457700

monoDet = myDetector('MONO_encoder')

pnccdDet = myDetector('pnccd')
andorDet = myDetector('andor')
# Path to the file with parameters of the experiment:
CALS = '/reg/d/psdm/sxr/sxrlq2715/scratch/cals/'
# Get integration limits from cals file
with open(CALS + 'limits.csv', 'rb') as csvfile:
	in_data = np.genfromtxt(csvfile, names=True, delimiter=',')

run_start_col = in_data['run_start']
run_end_col = in_data['run_end']

# Find the specified run number calibrations as the row which has a starting
# number less than or equal to the run number of interest and a ending
# number greater than or equal to the run number of interest (assumes that a
# given run will not fulfill [and should not fulfill!] these conditions for
# more than one row) - see original code "abs_XTC2HDF.py", line 81
rows_greater_or_equal = int(runnum) >= run_start_col
rows_less_or_equal = int(runnum) <= run_end_col
row_num_want = rows_greater_or_equal & rows_less_or_equal
run_cals = in_data[row_num_want]

mcp_limits = [run_cals['mcp_int_start'],run_cals['mcp_int_end'],run_cals['mcp_dead_start'],run_cals['mcp_dead_end']]
mcp4_limits = [run_cals['mcp4_int_start'],run_cals['mcp4_int_end'],run_cals['mcp4_dead_start'],run_cals['mcp4_dead_end']]
yag_limits = [run_cals['yag_int_start'],run_cals['yag_int_end'],run_cals['yag_dead_start'],run_cals['yag_dead_end']]
sin_limits = [run_cals['sin_int_start'],run_cals['sin_int_end'],run_cals['sin_dead_start'],run_cals['sin_dead_end']]
andor_limits = [run_cals['andorStart'],run_cals['andorEnd'],run_cals['andorbkgStart'],run_cals['andorbkgEnd']]

def acqiris_int(traces, int_limit):
	'Integration function for acqiris'

	subTrace_int = traces[int(int_limit[0]):int(int_limit[1])]
	subTrace_dead = traces[int(int_limit[2]):int(int_limit[3])]

	return np.sum(subTrace_int.astype(np.float64) - np.mean(subTrace_dead.astype(np.float64)))


# Binning against something
try:
	with open(CALS + 'run' + runnum + '.cfg', 'rb') as csvfile:
		binvalues = np.genfromtxt(csvfile, names=True, delimiter=',')
	binkey = binvalues.dtype.names[0]
	binvalues = binvalues[binkey]
	print('Binning data on '+binkey)
except:
	binvalues = None
	binkey = 'delay'

acq02Det = myDetector('Acq02')
acq01Det = myDetector('Acq01')
#magnetDet = myDetector('rci_magnet_voltage')
magnetDet = myDetector('SXR:EXP:AOT:04')
phasecavDet = myDetector('PhaseCavity')
delayStgDet = myDetector('SXR:LAS:MCN1:06.RBV')
waveplateDet = myDetector('SXR:LAS:MCN1:04.RBV')
vitaraDet = myDetector('LAS:FS2:VIT:FS_TGT_TIME')
vitaraLockedDet = myDetector('LAS:FS2:VIT:PHASE_LOCKED')
monoPVDet = myDetector('SXR:MON:MMS:06.RBV')
evrDet = myDetector('evr0')
gdeDet = myDetector('FEEGasDetEnergy')

# to use these check that tt_fltpos() is not None (only need to check 1)
tt_pxDet = myDetector('TTSPEC:FLTPOS')
tt_psDet = myDetector('TTSPEC:FLTPOS_PS')
tt_fwhmDet = myDetector('TTSPEC:FLTPOSFWHM')
tt_amplDet = myDetector('TTSPEC:AMPL')
#tt_refamplDet = myDetector('TTSPEC:REFAMPL')
#tt_amplnxtDet = myDetector('TTSPEC:TTSPEC:AMPLNXT')

smldata = dsource.small_data('run'+runnum+'.h5',gather_interval=1000)

timestamp0seconds = (datetime.datetime(2017,07,8,20,34) - datetime.datetime(1970,1,1)).total_seconds()

pnccdSumImg = None
pnccdSumImgnb = 0

andorSumImg = None
andorSumImgnb = 0

mcp4Sum = None
mcp4Sumnb = 0

sinSum = None
sinSumnb = 0

binnedpnccdP = None

mcp4threshold = -1
magnetthreshold = 0.5
adu_threshold = 500

eventToStartProcessingAt = 1000
eventToStopProcessingAt = 2000

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

for nevt,evt in enumerate(dsource.events()):

	if debug and nevt > 20:
		print('DEBUG: Break after 20 events')
		break

	if nevt % 20 == 0:
		print('Rank: {:d}, nevt: {:d}'.format(rank, nevt))

	#if(nevt > eventToStopProcessingAt):break	
	#if(nevt < eventToStartProcessingAt):continue

	evtId = evt.get(EventId)
	timestamp = evtId.time()[0] - timestamp0seconds + 1e-9*evtId.time()[1]

	#pnccd = pnccdDet[1].image(evt)
	try:
		temp = pnccdDet[1].photons(evt, adu_per_photon=adu_threshold)
	except:
		continue

	if temp is None:
		pnccd = None
	else:
		pnccd = pnccdDet[1].image(evt, temp)

	andor = andorDet[1].raw(evt)
	dls = dlsDet[1].get(evt)
	mono = monoDet[1].get(evt)
	acq02 = acq02Det[1].waveform(evt)
	acq01 = acq01Det[1].waveform(evt)
	magnet = magnetDet[1]()
	phasecav = phasecavDet[1].get(evt)
	delayStgPV = delayStgDet[1]()
	waveplatePV = waveplateDet[1]()
	vitaraPV = vitaraDet[1]()
	vitaraLockedPV = vitaraLockedDet[1]()
	monoPV = monoPVDet[1]()
	evr = evrDet[1].eventCodes(evt)
	gde = gdeDet[1].get(evt)

	if tt_psDet[0]:
		tt_px = tt_pxDet[1]()
		tt_ps = tt_psDet[1]()
		tt_fwhm = tt_fwhmDet[1]()
		tt_ampl = tt_amplDet[1]()

	#from IPython import embed
	#embed()

	# Skip event if while detector is present it returns None
	if pnccdDet[0] and (pnccd is None):
		continue
	if andorDet[0] and (andor is None):
		continue
	if dlsDet[0] and (dls is None):
		continue
	if monoDet[0] and (mono is None):
		continue
	if acq01Det[0] and (acq01 is None):
		continue
	if acq02Det[0] and (acq02 is None):
		continue
	if magnetDet[0] and (magnet is None):
		continue
	if phasecavDet[0] and (phasecav is None):
		continue
	if tt_psDet[0] and (tt_ps is None):
		continue
	if gdeDet[0] and (gde is None):
		continue
	if evrDet[0] and (evr is None):
		continue
	if delayStgDet[0] and (delayStgPV is None):
		continue
	if waveplateDet[0] and (waveplatePV is None):
		continue

	# Prepare to save data for this complete event
	myDictionary = {}
	myDictionary["timestamp"]= timestamp

	# Process event codes
	if 76 in evr:
		laser = 1
	elif 77 in evr:
		laser = 0
	else:
		laser = -1
	myDictionary["laser"] = laser

	if 162 in evr:
		bykick = 1
	else:
		bykick = 0
	myDictionary["bykick"] = bykick

	# Process andor if present
	if andorDet[0]:
		if andorSumImg is None:
			andorSumImg = andor.T.astype(np.double)
		else:
			andorSumImg += andor.T.astype(np.double)
		andorSumImgnb += 1

		myDictionary["transmission"] = acqiris_int(andor.T, andor_limits)

	# Process acqiris if present
	if acq02Det[0]:
		myDictionary["mcp"]= acqiris_int(acq02[0], mcp_limits)
		myDictionary["YAGTrans"]= acqiris_int(acq02[2], yag_limits)
		myDictionary["sin"]= acqiris_int(acq02[1], sin_limits)
		if sinSum is None:
			sinSum = acq02[1].astype(np.double)
		else:
			sinSum += acq02[1].astype(np.double)
		sinSumnb += 1
	
	if acq01Det[0]:
		myDictionary["mcp4"]= acqiris_int(acq01[2], mcp4_limits)
		if mcp4Sum is None:
			mcp4Sum = acq01[2].astype(np.double)
		else:
			mcp4Sum += acq01[2].astype(np.double)
		mcp4Sumnb += 1

	if dlsDet[0]:
		myDictionary["dls"] = dls.encoder_count()[0]

	if monoDet[0]:
		myDictionary["mono"] = mono.encoder_count()

	if phasecavDet[0]:
		myDictionary["phasecav"] = phasecav.fitTime2()

	if magnetDet[0]:
		myDictionary["magnet"] = magnet

	if delayStgDet[0]:
		myDictionary["delayStgPV"] = delayStgPV

	if waveplateDet[0]:
		myDictionary["waveplatePV"] = waveplatePV

	if monoPVDet[0]:
		myDictionary["monoPV"] = monoPV

	if vitaraDet[0]:
		myDictionary["vitaraPV"] = vitaraPV

	if vitaraLockedDet[0]:
		myDictionary["vitaraLockedPV"] = vitaraLockedPV

	if gdeDet[0]:
		enrc = 0.5*(gde.f_21_ENRC() + gde.f_22_ENRC())
		myDictionary["gde"] = enrc

	if tt_psDet[0]:
		myDictionary["tt_px"] = tt_px
		myDictionary["tt_ps"] = tt_ps
		myDictionary["tt_fwhm"] = tt_fwhm
		myDictionary["tt_amp"] = tt_ampl

	# Process pnccd if present
	if pnccdDet[0]:
		if pnccdSumImg is None:
			pnccdSumImg = pnccd.astype(np.double)
		else:
			pnccdSumImg += pnccd.astype(np.double)
		pnccdSumImgnb += 1

		if binvalues is None:
			# bin along single delay
			binvalues = np.array([myDictionary["vitaraPV"]])

		# find the proper bin index for this event
		# the first bin is for laser off
		if binkey == 'delay':
			binidx = np.argmin(np.abs(binvalues - myDictionary["vitaraPV"])) + 1
		elif binkey == 'laserdelay':
			binidx = np.argmin(np.abs(binvalues - (myDictionary["dls"] - TIME_ZERO)*PS_PER_ENC)) + 1
		elif binkey == 'magnet':
			# for each magnet value we have laser on/ laser off
			binidx = np.argmin(np.abs(binvalues - myDictionary["magnet"]))
			if myDictionary["laser"]:
				binidx = 2*binidx + 1
			else:
				binidx = 2*binidx
		else:
			binidx = 0

		if (not myDictionary["laser"]) and (binkey != 'magnet'):
			binidx = 0

		# allocate bin places
		if binnedpnccdP is None:
			v = np.shape(binvalues)[0]
			if binkey == 'magnet':
				v = 2*v
			else:
				v = v + 1
			binnedpnccdP = np.zeros((v, np.shape(pnccd)[0], np.shape(pnccd)[1]))
			binnedcountP = np.zeros((v))
			binnedmcp4P = np.zeros((v))
			binnedpnccdN = np.zeros((v, np.shape(pnccd)[0], np.shape(pnccd)[1]))
			binnedcountN = np.zeros((v))
			binnedmcp4N = np.zeros((v))
			binnedpnccdZ = np.zeros((v, np.shape(pnccd)[0], np.shape(pnccd)[1]))
			binnedcountZ = np.zeros((v))
			binnedmcp4Z = np.zeros((v))
			
		if (myDictionary["mcp4"] < mcp4threshold) and vitaraLockedPV:
			if binkey == 'magnet':
				binnedpnccdP[binidx,:,:] += pnccd
				binnedcountP[binidx] += 1
				binnedmcp4P[binidx] += myDictionary["mcp4"]
			else:
				if magnet > magnetthreshold:
					binnedpnccdP[binidx,:,:] += pnccd
					binnedcountP[binidx] += 1
					binnedmcp4P[binidx] += myDictionary["mcp4"]
				elif magnet < -magnetthreshold:
					binnedpnccdN[binidx,:,:] += pnccd
					binnedcountN[binidx] += 1
					binnedmcp4N[binidx] += myDictionary["mcp4"]
				else:
					binnedpnccdZ[binidx,:,:] += pnccd
					binnedcountZ[binidx] += 1
					binnedmcp4Z[binidx] += myDictionary["mcp4"]

	smldata.event(myDictionary)

# save HDF5 file, including summary data
summary = {}

if pnccdDet[0]:
	summary["pnccdSumImg"] = smldata.sum(pnccdSumImg/pnccdSumImgnb)/size
	
	summary["bin/pnccdP"] = smldata.sum(binnedpnccdP)
	summary["bin/countP"] = smldata.sum(binnedcountP)
	summary["bin/mcp4P"] = smldata.sum(binnedmcp4P)

	summary["bin/pnccdN"] = smldata.sum(binnedpnccdN)
	summary["bin/countN"] = smldata.sum(binnedcountN)
	summary["bin/mcp4N"] = smldata.sum(binnedmcp4N)

	summary["bin/pnccdZ"] = smldata.sum(binnedpnccdZ)
	summary["bin/countZ"] = smldata.sum(binnedcountZ)
	summary["bin/mcp4Z"] = smldata.sum(binnedmcp4Z)

	summary["bin/bins"] = binvalues
	summary["bin/key"] = binkey

if andorDet[0]:
	summary["andorSumImg"] = smldata.sum(andorSumImg/andorSumImgnb)/size

if acq01Det[0]:
	summary["mcp4Sum"] = smldata.sum(mcp4Sum/mcp4Sumnb)/size

if acq02Det[0]:
	summary["sinSum"] = smldata.sum(sinSum/sinSumnb)/size

smldata.save(summary)
smldata.close()
