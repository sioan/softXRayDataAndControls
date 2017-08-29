import numpy as np
from mpidata import mpidata 
import time

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import psana

def runclient(cfg):
    psana.setOption('psana.calib-dir', '/reg/d/psdm/sxr/sxrlq2715/calib')
    if cfg['shm']:
        ds = psana.DataSource('shmem=psana.0:stop=no')
    else:
        ds = psana.DataSource(cfg['psana_ds'])
    I0 = psana.Detector('Acq01')
    I1 = psana.Detector(cfg['ccd_name'])
    if (cfg['scan_key'] == 'mono'):
        scan_det = psana.Detector('SxrEndstation.0:USDUSB.0')
    elif (cfg['scan_key'] == 'delay'):
        scan_det = psana.Detector('DLS_encoder')
    elif (cfg['scan_key'] == 'magnet'):
        scan_det = psana.Detector('SXR:EXP:AOT:04')
    else:
        raise ValueError('Invalid scan key in configuration file')
    evr = psana.Detector('evr0')
    magnet = psana.Detector('SXR:EXP:AOT:04')
    I0_signals = np.array([])
    I1_signals = np.array([])
    MCP4_signals = np.array([])
    scan_vals = np.array([])
    laser_ons = np.array([])
    magnet_vals = np.array([])
    start_time = time.time()
    for nevent,evt in enumerate(ds.events()):
        if (not cfg['shm']):
            if nevent%(size-1)!=rank-1: 
                continue # different ranks look at different events        
        if I0.waveform(evt) is None:
            print 'NO I0'
            continue
        if I1.raw(evt) is None: 
            print 'NO I1' 
            continue
        if (cfg['scan_key'] == 'mono') or (cfg['scan_key'] == 'delay'):
            if scan_det.get(evt) is None:
                print 'NO '+cfg['scan_key']
                continue
        if evr.eventCodes(evt) is None: 
            print 'no EVR'
            continue
        if magnet() is None: 
            print 'no magnet'
            continue
        I0_signals = np.append(I0_signals, get_mcp_signal(I0, evt, cfg))
        MCP4_signals = np.append(MCP4_signals, get_mcp4_signal(I0, evt, cfg))
        I1_signals = np.append(I1_signals, get_ccd_signal(I1, evt, cfg))
        if (cfg['scan_key'] == 'mono'):
            scan_vals = np.append(scan_vals, scan_det.get(evt).encoder_count()[0])
        elif (cfg['scan_key'] == 'delay'):
            scan_vals = np.append(scan_vals, scan_det.get(evt).encoder_count()[0])
        elif (cfg['scan_key'] == 'magnet'):
            scan_vals = np.append(scan_vals, magnet())
        event_codes = evr.eventCodes(evt)
        laser_ons = np.append(laser_ons, (76 in event_codes))
        magnet_vals = np.append(magnet_vals, magnet())
        curr_time = time.time()
        if (curr_time-start_time >= cfg['update_period']):
            start_time = time.time()
            # send mpi data object to master when desired
            # Make a record array with data
            data_dict = {'I0': I0_signals,
                         'I1': I1_signals,
                         'MCP4': MCP4_signals,
                         'scan': scan_vals,
                         'laser_on': laser_ons,
                         'magnet': magnet_vals}
            data = np.rec.fromarrays(data_dict.values(), names=data_dict.keys())
            print len(data)
            comm.send(data, dest=0, tag=rank)
            # Reset data arrays:
            I0_signals = np.array([])
            I1_signals = np.array([])
            MCP4_signals = np.array([])
            scan_vals = np.array([])
            laser_ons = np.array([])
            magnet_vals = np.array([])

def get_mcp_signal(det, evt, cfg):
    mcp_waveform = det.waveform(evt)[cfg['mcp_chan']]
    mcp_sig = np.mean(mcp_waveform[cfg['mcp_sig_start']:cfg['mcp_sig_end']])
    mcp_dead = np.mean(mcp_waveform[cfg['mcp_dead_start']:cfg['mcp_dead_end']])
    mcp_val = -1*(mcp_sig-mcp_dead)
    return mcp_val

def get_mcp4_signal(det, evt, cfg):
    mcp4_waveform = det.waveform(evt)[cfg['mcp4_chan']]
    mcp4_sig1 = np.mean(mcp4_waveform[cfg['mcp4_sig1_start']:cfg['mcp4_sig1_end']])
    mcp4_sig2 = np.mean(mcp4_waveform[cfg['mcp4_sig2_start']:cfg['mcp4_sig2_end']])
    mcp4_sig3 = np.mean(mcp4_waveform[cfg['mcp4_sig3_start']:cfg['mcp4_sig3_end']])
    mcp4_sig4 = np.mean(mcp4_waveform[cfg['mcp4_sig4_start']:cfg['mcp4_sig4_end']])
    mcp4_dead = np.mean(mcp4_waveform[cfg['mcp4_dead_start']:cfg['mcp4_dead_end']])
    mcp4_val = -1*(mcp4_sig1+mcp4_sig2+mcp4_sig3+mcp4_sig4-4*mcp4_dead)
    return mcp4_val
    
def get_ccd_signal(det, evt, cfg):
    ccd_image = det.raw(evt)
    ccd_sig = np.mean(ccd_image[cfg['ccd_sig_top']:cfg['ccd_sig_bottom'], cfg['ccd_sig_left']:cfg['ccd_sig_right']])
    ccd_dead = np.mean(ccd_image[cfg['ccd_dead_top']:cfg['ccd_dead_bottom'], cfg['ccd_dead_left']:cfg['ccd_dead_right']])
    ccd_val = ccd_sig-ccd_dead
    return ccd_val
