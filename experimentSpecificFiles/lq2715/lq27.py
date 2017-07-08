import numpy as np
import h5py

# Functions commonly used at LCLS, but also generically applicable
def weighted_std(values, weights):
    """Calculate the weighted standard deviation of values
    """
    weighted_mean = np.average(values, weights=weights)
    weighted_mean_squared = np.average(values**2, weights=weights)
    got_weighted_std = np.sqrt(weighted_mean_squared-weighted_mean**2)
    return got_weighted_std

def norm_hist(bin_data, sigs, norms, bins=100,
              bin_length=None):
    """Return normalized histograms
    """
    data = weight_hist(bin_data, sigs/norms, norms, bins,
                       bin_length)
    return data

def weight_hist(bin_data, sigs, weights, bins=100,
                bin_length=None):
    """Return weighted mean and std of sigs for each bin
    """
    if bin_length is not None:
        bin_start = np.amin(bin_data)
        bin_end = np.amax(bin_data)
        bins = np.arange(bin_start, bin_end+bin_length, bin_length)
    elif np.size(bins) == 1:
        bin_start = np.amin(bin_data)
        bin_end = np.amax(bin_data)
        bins = np.linspace(bin_start, bin_end, bins)
    bin_centers = (bins[1:]+bins[:-1])/2
    bin_counts, unused = np.histogram(bin_data,
                                      bins=bins)
    weight_sig_sums, unused = np.histogram(bin_data,
                                   weights=sigs*weights,
                                   bins=bins)
    weight_sums, unused = np.histogram(bin_data,
                               weights=weights,
                               bins=bins)
    weight_sig_mean = weight_sig_sums/weight_sums
    weight_sig_squared_sums, unused = np.histogram(bin_data,
                                           weights=sigs**2*weights,
                                           bins=bins)
    weight_sig_squared_mean = weight_sig_squared_sums/weight_sums
    weight_sig_var = (weight_sig_squared_mean-weight_sig_mean**2)
    # weight_sig_std is the weighted standard deviation and is
    # computed following the formula on the Wikipedia entry for
    # mean square weighted deviation
    weight_sig_std = np.sqrt(weight_sig_var)
    weight_sig_std = weight_sig_std/np.sqrt(bin_counts)
    data = {'bin_edges': bins,
            'bin_centers': bin_centers,
            'norm_sig': weight_sig_mean,
            'err': weight_sig_std,
            'norm_sums': weight_sums,
            'bin_counts': bin_counts}
    return data

# Path to the directory with data
DATA_PATH = '/reg/d/psdm/sxr/sxrlq2715/hdf5/smalldata/'
# The number of delay stage, in ps per encoder units
PS_PER_ENC = 1.33426e-4
# The approximate position of time zero, in encoder units
TIME_ZERO = -6457700
# The laser on/off event code numbers
LASER_ON_CODE = 76 # 76 in EVR
LASER_OFF_CODE = 77 # 77 in EVR

# Loading smalldata h5 file
def load_data(run, tc_on=True, tc_type='pc', folder=DATA_PATH):
	""" Load a smalldata h5 file

		Arguments:
			run: integer, run number
			tc_on: boolean, time correction on or off
			tc_type: string, type of time correction, either 'tt' for time tool or 'pc' for phase cavity

		Output:
			data: record array of the loaded data
	"""

	file_name = 'run{:d}.h5'.format(run)
	f = h5py.File(folder+file_name, 'r')
	#----- Phase Cavity
	phasecav_data = f['phasecav'].value
	num_events = len(phasecav_data) # we should always have "phasecav_data"
	print('Events found: ' + str(num_events))
	#----- Delay Stage Encoder
	ds_encoder_data = (f['dls'].value - TIME_ZERO)*PS_PER_ENC
	#----- Delay Stage PV
	ds_pv_data = f['delayStgPV'].value
	#----- Monochromator Encoder
	try:
		#mono_encoder_completeData = f['mono'].value
		#mono_encoder_data = (mono_encoder_completeData[:,0]*PHOT_SCALE) - PHOT_SHIFT # CHECK THE COLUMN (0 should be fine)
		mono_enc = f['mono'].value[:,0] - f['mono'].value[:,1] 
	except:
		mono_enc = np.zeros(num_events)

	#----- Monochromator PV
	mono_pv_data = f['monoPV'].value
	#----- Magnet Voltage
	#magnet_data = f['magnet'].value
	#----- Time Tool
	try:
		tt_px_data = f['tt_px'].value
		tt_ps_data = f['tt_ps'].value
		tt_fwhm_data = f['tt_fwhm'].value
		tt_amp_data = f['tt_amp'].value
	except:
		tt_px_data = np.zeros(num_events)
		tt_ps_data = np.zeros(num_events)
		tt_fwhm_data = np.zeros(num_events)
		tt_amp_data = np.zeros(num_events)
	#----- MCP monitor
	try:
		mcp_data = -1.0*f['mcp'].value
	except:
		mcp_data = np.zeros(num_events)

	try:
		mcp4_data = -1.0*f['mcp4'].value
	except:
		mcp4_data = np.zeros(num_events)

	#----- YAG transmission monitor
	try:
		YAGTrans = f['YAGTrans'].value
	except:
		YAGTrans = np.zeros(num_events)

	#----- Si3N4
	try:
		sin = f['sin'].value
	except:
		sin = np.zeros(num_events)

	#----- X-Ray Status
	try:
		xray_data = f['bykick'].value
		xray_bool = np.array(xray_data == XRAY_ON_CODE)
	except:
		xray_bool = np.ones(num_events,dtype=bool)

	#----- pnCCD Detector (Transmitted X-ray Intensity)
	try:
		signal = f['signal'].value
	except:
		signal = np.zeros(num_events)
	try:
		reference = f['reference'].value
	except:
		reference = np.zeros(num_events)
	try:
		dark = f['dark'].value
	except:
		dark = np.zeros(num_events)

	#----- Laser Status
	laser_data = f['code'].value
	laser_bool = np.array(laser_data == LASER_ON_CODE)

	#----- GMD
	try:
		gmd_data = f['gde'].value
	except:
		gmd_data = np.zeros(num_events)

	#----- Vitara
	try:
		vitara_data = f['vitaraPV'].value
	except:
		vitara_data = np.zeros(num_events)

	#----- laser waveplate
	try:
		waveplate = f['waveplatePV'].value
	except:
		waveplate = np.zeros(num_events)
	#----- timestamp
	try:
		timestamp = f['timestamp'].value
	except:
		timestamp = np.zeros(num_events)

	#----- Run Column
	run_data = np.array([run]*num_events)
	#----- Sequential number
	seq_data = np.array(range(num_events))

	# Time Tool and Phase Cavity for correction and filtering
	ttpc_data = tt_ps_data + phasecav_data 

	# Time Correction
	if tc_on:
		if tc_type == 'tt':
			ds_encoder_data = ds_encoder_data - tt_ps_data
			print('Time Tool and Phase Cavity Correction')
		elif tc_type == 'pc':
			ds_encoder_data = ds_encoder_data - phasecav_data
			print('Phase Cavity Correction')
		else:
			print('Time correction NOT FOUND')

	# Combine the data into a numpy record array
	names_list = ['evt','run','mcp','mcp4','signal', 'reference', 'dark', 'delay', 'phasecav','tt_px','tt_ps', 'tt_fwhm', 'tt_amp',
		'delay_pv','mono_pv','mono_enc','laser_evt','xray_evt','ttpc','gmd','YAGTrans','sin','timestamp','vitara','waveplate']
	arr_list = [seq_data,run_data, mcp_data, mcp4_data, signal, reference, dark, ds_encoder_data, phasecav_data, tt_px_data, tt_ps_data, tt_fwhm_data, tt_amp_data,
		 ds_pv_data, mono_pv_data, mono_enc, laser_bool, xray_bool, ttpc_data, gmd_data,YAGTrans,sin,timestamp,vitara_data,waveplate]
	out_data  = np.rec.fromarrays(arr_list, names=names_list)
	return out_data

# Filter function
def data_filter(data, key, low_level = None, high_level = None):
    """ General Filter in data such that low < data['key'] < kigh
    """

    num_points = len(data['run'])
    #print('Events before '+key+' filtering: {:d}'.format(num_points))
    if low_level is None:
        low_filter = np.ones(num_points, dtype=bool)
    else:
        low_filter = data[key] > low_level

    if high_level is None:
        high_filter = np.ones(num_points, dtype=bool)
    else:
        high_filter = data[key] < high_level
        
    data = data[np.logical_and(low_filter, high_filter)]
    
    #print('Events after '+key+' filtering: {:d}'.format(len(data['run'])))
    return data

from scipy.stats import scoreatpercentile
# Filter out potentially problematic/poorer quality data (MCP Filter)
def mcp_filter(data, low_int_filt=30, high_int_filt=95, I0_KEY = 'mcp4'):
    """ Filter out potentially problematic/poorer quality data
    """
    
    #print('Events before MCP filtering: {:d}'.format(len(data['run'])))
    mcp_too_high = scoreatpercentile(data[I0_KEY], high_int_filt)
    mcp_too_low = scoreatpercentile(data[I0_KEY], low_int_filt)
    mcp_filt = np.logical_and(data[I0_KEY] > mcp_too_low,  data[I0_KEY] < mcp_too_high)
    data = data[mcp_filt]
    #print('Events after MCP filtering: {:d}'.format(len(data['run'])))
    return data

# Not sure this is phasecav_filter make sense
# def phasecav_filter(data, low=-0.5, high=0.5):
#    'Filter out potentially problematic/poorer quality data'
#    
#    print('Events before Phasecav filtering: {:d}'.format(len(data['run'])))
#    delay = data['delay'] - data['phasecav']
#    m = np.median(delay)
#    filt = np.logical_and(delay < m + high,  delay > m + low)
#    data = data[filt]
#    print('Events after Phasecav filtering: {:d}'.format(len(data['run'])))
#    return data


# Data binning according to type of scan (energy spectrum, time delay, ...)

from numpy.lib.recfunctions import append_fields

# Get XAS spectrum
def get_XAS_spectrum(data_in, num_bins=100, energy_limits=None,
        NRJ_KEY = 'mono_enc', NRJ2eVfunc=lambda x: x, I0_KEY = 'mcp4'):
    'Get a XAS spectrum'

    data = append_fields(data_in, 'mono_pv_eV', NRJ2eVfunc(data_in[NRJ_KEY]))
    
    if energy_limits is None:
        energy_limits = [np.amin(data['mono_pv_eV']), np.amax(data['mono_pv_eV'])]

    energy_range = np.linspace(energy_limits[0],energy_limits[1],num_bins+1)

    # Get the spectral data
    spectrum =  norm_hist(data['mono_pv_eV'], data['signal'], data[I0_KEY], bins=energy_range)

    phot_data = spectrum['bin_centers']
    spec_out = -1.0*np.log(spectrum['norm_sig'])

    run_data = np.full_like(phot_data, data['run'][0])

    names_list = ['run','phot', 'intensity']
    arr_list = [run_data, phot_data, spec_out]
    out_data = np.rec.fromarrays(arr_list, names=names_list)
    return out_data

# Get the time delay scan
def get_time_delay(data_in, key = 'YAGTrans', bins=None, YAG=False, I0_KEY = 'mcp4'):
    'Get the time delay scan'

    # Get the time delay scan
    if YAG:
        normby = np.ones_like(data_in['delay'])
    else:
        normby = data_in[I0_KEY]

    if bins is not None:
        delay_data = norm_hist(data_in['delay'], data_in[key], normby, bins=bins)
    else:
        delay_data = norm_hist(data_in['delay'], data_in[key], normby, bin_length=0.1)

    if YAG:
        delay_data['abs'] = delay_data['norm_sig']
    else:
        delay_data['abs'] = -1.0*np.log(delay_data['norm_sig'])

    delay_data['abs_err'] = delay_data['err']/delay_data['norm_sig'] # TO BE CHECKED (we have a np.log in 'abs')
    delay_data['delay'] = delay_data['bin_centers']

    return delay_data

def get_Energy_Time_spectrum(data, energy_bins, delay_bins, mono='mono_pv'):

	H, nrj, delay = np.histogram2d(data[mono], data['delay'], bins=(energy_bins, delay_bins),
		weights=-np.log(data['signal']/data['reference']))
	counts, nrj, delay = np.histogram2d(data[mono], data['delay'], bins=(energy_bins, delay_bins))

	return H/counts, nrj, delay, counts

# Get COMPLETE spectrum
def get_nosample_spectrum(data_in, num_bins=100, energy_limits=None,
        NRJ_KEY = 'mono_enc', NRJ2eVfunc=lambda x: x, I0_KEY = 'mcp4'):
    'Get nosample spectrum'

    data = append_fields(data_in, 'mono_pv_eV', NRJ2eVfunc(data_in[NRJ_KEY]))

    if energy_limits is None:
        energy_limits = [np.amin(data['mono_pv_eV']), np.amax(data['mono_pv_eV'])]

    energy_range = np.linspace(energy_limits[0],energy_limits[1],num_bins+1)

    # Get the spectral data
    spectrum =  norm_hist(data['mono_pv_eV'], data['T'], data[I0_KEY], bins=energy_range)
    phot_data = spectrum['bin_centers']
    spec = -1.0*np.log(spectrum['norm_sig'])
    
    run_data = np.full_like(phot_data, data['run'][0])

    names_list = ['run','phot','absorption']
    arr_list = [run_data,phot_data,spec]
    out_data = np.rec.fromarrays(arr_list, names=names_list)
    return out_data


# Get the time delay scan for a particular run and parameters ("xmcd_ana2.py")
def get_time_delay_scan(data_in, magnet_dir=None, pumped=None, bins=None, YAG=False,
        I0_KEY = 'mcp4', MAG_VOLT_THRESH = 1.0):
    'Get the time delay scan for a particular run and parameters'

    if magnet_dir is None:
        data = data_in
    elif magnet_dir > 0:
        data = data_filter(data_in, 'magnet', low_level = MAG_VOLT_THRESH)
    else:
        data = data_filter(data_in, 'magnet', high_level = -MAG_VOLT_THRESH)

    if pumped is not None:
        if pumped:
            data = data_filter(data, 'laser_evt', low_level = 0.5)
        else:
            data = data_filter(data, 'laser_evt', high_level = 0.5)

    # Get the time delay scan
    if YAG:
        key = 'YAGTrans'
        normby = np.ones_like(data['delay'])
    else:
        key = 'T'
        normby = data[I0_KEY]

    if bins is not None:
        delay_data = norm_hist(data['delay'], data[key], normby, bins=bins)
    else:
        delay_data = norm_hist(data['delay'], data[key], normby, bin_length=0.1)

    if YAG:
        delay_data['abs'] = delay_data['norm_sig']
    else:
        delay_data['abs'] = -1.0*np.log(delay_data['norm_sig'])

    delay_data['abs_err'] = delay_data['err']/delay_data['norm_sig'] # TO BE CHECKED (we have a np.log in 'abs')
    delay_data['delay'] = delay_data['bin_centers']
    return delay_data

# Get LASER ON / LASER OFF delay curve (no filtering on magnet)
def get_lasONlasOFF_delay(data, bin_range=np.arange(-30, 30, 0.1), subdividerunby=1, YAG=False,
        I0_KEY = 'mcp4', MAG_VOLT_THRESH = 1.0):
    'Get LASER ON / LASER OFF delay curve (no filtering on magnet'
    #HERE, bins will be an ARANGE

    N = int(len(data)/subdividerunby)
    out_data = []
    for k in range(subdividerunby):
        if k == (subdividerunby - 1):
            data_in = data[(k*N):]
        else:
            data_in = data[(k*N):((k+1)*N - 1)]

        delay_lon_data = get_time_delay_scan(data_in, magnet_dir=None, pumped=True, bins=bin_range,
            YAG=YAG, I0_KEY=I0_KEY, MAG_VOLT_THRESH=MAG_VOLT_THRESH)
        delay_loff_data = get_time_delay_scan(data_in, magnet_dir=None, pumped=False, bins=bin_range,
            YAG=YAG, I0_KEY=I0_KEY, MAG_VOLT_THRESH=MAG_VOLT_THRESH)
        delay_data = delay_lon_data['delay']
        delay_lon_out = delay_lon_data['abs'] 
        delay_loff_out = delay_loff_data['abs']
        num_points = len(delay_data)
        run_data = np.array([data_in['run'][0]]*num_points)

        names_list = ['run','delay','lasON','lasOFF']
        arr_list = [run_data,delay_data,delay_lon_out,delay_loff_out]
        out_data.append(np.rec.fromarrays(arr_list, names=names_list))
    
    if subdividerunby == 1:
        return out_data[0]
    else:
        return out_data
    
# Get XMCD delay curve (COMPLETE)
def get_xmcd_delay(data, bin_range=np.arange(-30, 30, 0.1), subdividerunby=1, t0shifts=None,
        I0_KEY = 'mcp4', MAG_VOLT_THRESH = 1.0):
    'Get XMCD delay curve (COMPLETE)'
    #HERE, bins will be an ARANGE

    if not(t0shifts is None):
        LT = len(t0shifts)
        N = len(data)/LT
        bounds = [int(np.round(k*N)) for k in range(LT)]
        for k in range(LT):
            if k == (LT - 1):
                data[bounds[k]:]['delay'] -= t0shifts[k]
            else:
                data[bounds[k]:(bounds[k+1] - 1)]['delay'] -= t0shifts[k]

    N = len(data)/subdividerunby
    out_data = []
    bounds = [int(np.round(k*N)) for k in range(subdividerunby)]
    for k in range(subdividerunby):
        if k == (subdividerunby - 1):
            data_in = data[bounds[k]:]
        else:
            data_in = data[bounds[k]:(bounds[k+1] - 1)]

        delay_mp_lon_data = get_time_delay_scan(data_in, magnet_dir=1, pumped=True, bins=bin_range,
                I0_KEY=I0_KEY, MAG_VOLT_THRESH=MAG_VOLT_THRESH)
        delay_mm_lon_data = get_time_delay_scan(data_in, magnet_dir=-1, pumped=True, bins=bin_range,
                I0_KEY=I0_KEY, MAG_VOLT_THRESH=MAG_VOLT_THRESH)
        delay_mp_loff_data = get_time_delay_scan(data_in, magnet_dir=1, pumped=False, bins=bin_range, I0_KEY=I0_KEY, MAG_VOLT_THRESH=MAG_VOLT_THRESH)
        delay_mm_loff_data = get_time_delay_scan(data_in, magnet_dir=-1, pumped=False, bins=bin_range, I0_KEY=I0_KEY, MAG_VOLT_THRESH=MAG_VOLT_THRESH)

        delay_xmcd_data = delay_mp_lon_data['delay']
        delay_mp_lon_out = delay_mp_lon_data['abs']
        delay_mm_lon_out = delay_mm_lon_data['abs']
        delay_mp_loff_out = delay_mp_loff_data['abs']
        delay_mm_loff_out = delay_mm_loff_data['abs']
        num_points = len(delay_xmcd_data)
        run_data = np.array([data_in['run'][0]]*num_points)

        names_list = ['run','delay','magnPlasON','magnMlasON','magnPlasOFF','magnMlasOFF']
        arr_list = [run_data,delay_xmcd_data,delay_mp_lon_out,delay_mm_lon_out,delay_mp_loff_out,delay_mm_loff_out]
        out_data.append(np.rec.fromarrays(arr_list, names=names_list))

    if subdividerunby == 1:
        return out_data[0]
    else:
        return out_data
