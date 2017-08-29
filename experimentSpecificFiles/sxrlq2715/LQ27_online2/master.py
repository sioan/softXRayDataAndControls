from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from psmon import publish
import psmon.plots as psplt
import h5py
import numpy as np
from mpidata import mpidata 
import time

from corr_stats import CorrStats
from xmcd_scan import XmcdScan

#import pyca
#from caput import caput

def runmaster(nClients, cfg):
    data_list = []
    corr_obj = CorrStats(x_name='MCP',
                         y_name=cfg['ccd_name'],
                         plots_name=cfg['ccd_name']+' vs MCP',
                         perc_too_high=95,
                         perc_too_low=30)
    corr_obj2 = CorrStats(x_name='MCP4',
                          y_name=cfg['ccd_name'],
                          plots_name=cfg['ccd_name']+' vs MCP4',
                          perc_too_high=95,
                          perc_too_low=30)
    corr_obj3 = CorrStats(x_name='MCP', y_name='MCP4',
                          plots_name='MCP4 vs MCP',
                          perc_too_high=95,
                          perc_too_low=30)
    xmcd_obj = XmcdScan(cfg['scan_key'], cfg['scan_start'], cfg['scan_stop'], cfg['num_bins'], cfg['magnet_threshold'])
    start_time = time.time()
    while nClients > 0:
        # Remove client if the run ended
        status = MPI.Status()
        curr_data = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        data_list.append(curr_data)
        curr_time = time.time()
        if (curr_time-start_time >= cfg['update_period']):
            data = np.hstack(data_list)
            corr_obj.upd_corr_stats(data['I0'], data['I1'])
            corr_obj.publish_corr_plots()
            corr_obj2.upd_corr_stats(data['MCP4'], data['I1'])
            corr_obj2.publish_corr_plots()
            corr_obj3.upd_corr_stats(data['I0'], data['MCP4'])
            corr_obj3.publish_corr_plots()
            xmcd_obj.upd_traces(data)
            xmcd_obj.publish_traces()
            data_list = []
            start_time = time.time()
            numerator = np.sum(data['I1'])
            denominator = np.sum(data['I0'])
            ratio = numerator/denominator
            #try:
            #    caput('SXR:TST:RBV:2', ratio)
            #except pyca.pyexc, e:
            #    print 'Failed to connect to a PV ',e
            #except pyca.caexc, e:
            #    print 'Channel access error', e
            print 'Updated!'

def plot_corr(data):
    pass

def plot_scan(data):
    pass
