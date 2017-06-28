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
dsource = MPIDataSource('exp=sxrx22915:run='+runnum+':smd:dir=/reg/d/ffb/sxr/sxrx22915/xtc:live')
#After beamtime
#dsource = MPIDataSource('exp=sxrx22915:run='+runnum+':smd')

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
	return (False, Detector(name))

dlsDet = myDetector('DLS_encoder')
monoDet = myDetector('MONO_encoder')

pnccdDet = myDetector('pnccd')
# Path to the file with parameters of the experiment:
CALS = '/reg/d/psdm/sxr/sxrx22915/scratch/cals/limits.csv'
# Get integration limits from cals file
with open(CALS, 'rb') as csvfile:
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
x1Start, x1End, y1Start, y1End = [run_cals['x1Start'],run_cals['x1End'],run_cals['y1Start'],run_cals['y1End']]
x2Start, x2End, y2Start, y2End = [run_cals['x2Start'],run_cals['x2End'],run_cals['y2Start'],run_cals['y2End']]
x3Start, x3End, y3Start, y3End = [run_cals['x3Start'],run_cals['x3End'],run_cals['y3Start'],run_cals['y3End']]

def acqiris_int(traces, int_limit):
	'Integration function for acqiris'

	subTrace_int = traces[int(int_limit[0]):int(int_limit[1])]
	subTrace_dead = traces[int(int_limit[2]):int(int_limit[3])]

	return np.sum(subTrace_int.astype(np.float64) - np.mean(subTrace_dead.astype(np.float64)))

acq02Det = myDetector('Acq02')
acq01Det = myDetector('Acq01')
#magnetDet = myDetector('rci_magnet_voltage')
phasecavDet = myDetector('PhaseCavity')
delayStgDet = myDetector('SXR:LAS:MCN1:06.RBV')
vitaraDet = myDetector('LAS:FS2:VIT:FS_TGT_TIME')
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

timestamp0seconds = (datetime.datetime(2017,06,21,20,34) - datetime.datetime(1970,1,1)).total_seconds()

pnccdSumImg = None
mcp4Sum = None
sinSum = None

for nevt,evt in enumerate(dsource.events()):

	if debug and nevt > 10:
		print('DEBUG: Break after 10 events')
		break

	evtId = evt.get(EventId)
	timestamp = evtId.time()[0] - timestamp0seconds + 1e-9*evtId.time()[1]

	pnccd = pnccdDet[1].image(evt)
	dls = dlsDet[1].get(evt)
	mono = monoDet[1].get(evt)
	acq02 = acq02Det[1].waveform(evt)
	acq01 = acq01Det[1].waveform(evt)
	#magnet = magnetDet[1]()
	phasecav = phasecavDet[1].get(evt)
	delayStgPV = delayStgDet[1]()
	vitaraPV = vitaraDet[1]()
	monoPV = monoPVDet[1]()
	evr = evrDet[1].eventCodes(evt)
	gde = gdeDet[1].get(evt)

	tt_px = tt_pxDet[1]()
	tt_ps = tt_psDet[1]()
	tt_fwhm = tt_fwhmDet[1]()
	tt_ampl = tt_amplDet[1]()

	#from IPython import embed
	#embed()

	# Skip event if while detector is present it returns None
	if pnccdDet[0] and (pnccd is None):
		continue
	if dlsDet[0] and (dls is None):
		continue
	if monoDet[0] and (mono is None):
		continue
	if acq01Det[0] and (acq01 is None):
		continue
	if acq02Det[0] and (acq02 is None):
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

	# Prepare to save data for this complete event
	myDictionary = {}
	myDictionary["timestamp"]= timestamp

	# Process event codes
	if 76 in evr:
		code = 76
	elif 77 in evr:
		code = 77
	else:
		code = 0
	myDictionary["code"] = code

	if 162 in evr:
		bykick = 1
	else:
		bykick = 0
	myDictionary["bykick"] = bykick


	# Process pnccd if present
	if pnccdDet[0]:
		if pnccdSumImg is None:
			pnccdSumImg = pnccd.astype(np.double)
		else:
			pnccdSumImg += pnccd.astype(np.double)

		signal = np.sum(pnccd[int(y1Start):int(y1End),int(x1Start):int(x1End)])
		reference = np.sum(pnccd[int(y2Start):int(y2End),int(x2Start):int(x2End)])
		dark = np.sum(pnccd[int(y3Start):int(y3End),int(x3Start):int(x3End)])

		myDictionary["signal"]= signal
		myDictionary["reference"]= reference
		myDictionary["dark"]= dark

	# Process acqiris if present
	if acq02Det[0]:
		myDictionary["mcp"]= acqiris_int(acq02[0], mcp_limits)
		myDictionary["YAGTrans"]= acqiris_int(acq02[2], yag_limits)
		myDictionary["sin"]= acqiris_int(acq02[1], sin_limits)
		if sinSum is None:
			sinSum = acq02[1].astype(np.double)
		else:
			sinSum += acq02[1].astype(np.double)
	
	if acq01Det[0]:
		myDictionary["mcp4"]= acqiris_int(acq01[2], mcp4_limits)
		if mcp4Sum is None:
			mcp4Sum = acq01[2].astype(np.double)
		else:
			mcp4Sum += acq01[2].astype(np.double)

	if dlsDet[0]:
		myDictionary["dls"] = dls.encoder_count()[0]

	if monoDet[0]:
		myDictionary["mono"] = mono.encoder_count()

	if phasecavDet[0]:
		myDictionary["phasecav"] = phasecav.fitTime2()

	if delayStgDet[0]:
		myDictionary["delayStgPV"] = delayStgPV

	if monoPVDet[0]:
		myDictionary["monoPV"] = monoPV

	if vitaraDet[0]:
		myDictionary["vitaraPV"] = vitaraPV

	if gdeDet[0]:
		enrc = 0.5*(gde.f_21_ENRC() + gde.f_22_ENRC())
		myDictionary["gde"] = enrc

	if tt_psDet[0]:
		myDictionary["tt_px"] = tt_px
		myDictionary["tt_ps"] = tt_ps
		myDictionary["tt_fwhm"] = tt_fwhm
		myDictionary["tt_amp"] = tt_ampl

	smldata.event(myDictionary)

# save HDF5 file, including summary data
summary = {}

if pnccdDet[0]:
	summary["pnccdSumImg"] = smldata.sum(pnccdSumImg)

if acq01Det[0]:
	summary["mcp4Sum"] = smldata.sum(mcp4Sum)

if acq02Det[0]:
	summary["sinSum"] = smldata.sum(sinSum)

smldata.save(summary)
smldata.close()
