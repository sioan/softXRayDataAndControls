"""Class to keep track of, calculate, and plot normalized histograms
of an XMCD scan with data being continuously fed in.

Daniel Higley: 2016-10
"""

import numpy as np
import scipy.stats

print 'IMPORTING LCLS MODULES...'
from psmon import publish
from psmon.plots import XYPlot, Image, Hist, MultiPlot
publish.init(port=12301, local=True)
print 'DONE'
print 'Starting server'
print 'Setting ZMQ publishing'

class XmcdScan:
    def __init__(self, scan_var_key='scan', scan_var_start=0,
                 scan_var_stop=1, num_bins=100, mag_thresh=0.08, 
                 perc_too_high=95,
                 perc_too_low=30):
        self.scan_key = scan_var_key
        # Calculate bin edges
        self.bin_edges = np.linspace(scan_var_start, scan_var_stop, num_bins)
        self.mag_thresh = mag_thresh
        # Initialize histograms
        self.lon_hists = {'norm_mp': np.zeros(len(self.bin_edges)-1),
                          'norm_mm': np.zeros(len(self.bin_edges)-1),
                          'signal_mp': np.zeros(len(self.bin_edges)-1),
                          'signal_mm': np.zeros(len(self.bin_edges)-1)}
        self.loff_hists = {'norm_mp': np.zeros(len(self.bin_edges)-1),
                           'norm_mm': np.zeros(len(self.bin_edges)-1),
                           'signal_mp': np.zeros(len(self.bin_edges)-1),
                           'signal_mm': np.zeros(len(self.bin_edges)-1)}

        pass

    def upd_traces(self, data):
        """Update histograms of data
        """
        if len(data) == 0:
            # No data recorded, no need to update data
            pass
        # Intensity filter data
        too_high = scipy.stats.scoreatpercentile(data['I0'], 95)
        too_low = scipy.stats.scoreatpercentile(data['I0'], 30)
        filt_idx = (data['I0'] > too_low) & (data['I0'] < too_high)
        data = data[filt_idx]
        # Separate data into laser on and laser off data
        lon_data = data[data['laser_on'].astype(bool)]
        loff_data = data[np.logical_not(data['laser_on'])]
        if self.scan_key == 'magnet':
           # Hack to not separate data by magnetization when scanning
           # magnet while still being compatible with rest of code
           lon_mp_data = lon_data
           lon_mm_data = lon_data
           loff_mp_data = loff_data
           loff_mm_data = loff_data
        else:
            # Separate data into magnetization + and - 
            lon_mp_data = lon_data[lon_data['magnet'] > self.mag_thresh]
            lon_mm_data = lon_data[lon_data['magnet'] < -1*self.mag_thresh]
            loff_mp_data = loff_data[loff_data['magnet'] > self.mag_thresh]
            loff_mm_data = loff_data[loff_data['magnet'] < -1*self.mag_thresh]
        # Update histograms
        self.lon_hists['norm_mp'] += np.histogram(lon_mp_data['scan'],
                                                  bins=self.bin_edges,
                                                  weights=lon_mp_data['I0'])[0]
        self.lon_hists['norm_mm'] += np.histogram(lon_mm_data['scan'],
                                                  bins=self.bin_edges,
                                                  weights=lon_mm_data['I0'])[0]
        self.lon_hists['signal_mp'] += np.histogram(lon_mp_data['scan'],
                                                    bins=self.bin_edges,
                                                    weights=lon_mp_data['I1'])[0]
        self.lon_hists['signal_mm'] += np.histogram(lon_mm_data['scan'],
                                                    bins=self.bin_edges,
                                                    weights=lon_mm_data['I1'])[0]
        self.loff_hists['norm_mp'] += np.histogram(loff_mp_data['scan'],
                                                  bins=self.bin_edges,
                                                  weights=loff_mp_data['I0'])[0]
        self.loff_hists['norm_mm'] += np.histogram(loff_mm_data['scan'],
                                                  bins=self.bin_edges,
                                                  weights=loff_mm_data['I0'])[0]
        self.loff_hists['signal_mp'] += np.histogram(loff_mp_data['scan'],
                                                    bins=self.bin_edges,
                                                    weights=loff_mp_data['I1'])[0]
        self.loff_hists['signal_mm'] += np.histogram(loff_mm_data['scan'],
                                                    bins=self.bin_edges,
                                                    weights=loff_mm_data['I1'])[0]

    def publish_traces(self):
        # Calculate accumulated absorptions:
        abs_lon_mp = -np.log(self.lon_hists['signal_mp']/self.lon_hists['norm_mp'])
        abs_lon_mm = -np.log(self.lon_hists['signal_mm']/self.lon_hists['norm_mm'])
        abs_loff_mp = -np.log(self.loff_hists['signal_mp']/self.loff_hists['norm_mp'])
        abs_loff_mm = -np.log(self.loff_hists['signal_mm']/self.loff_hists['norm_mm'])
        # Make MultiPlot to hold plots:
        plots_title = 'XMCD Scan'
        xmcd_plots = MultiPlot(plots_title, plots_title, ncols=3)
        # Make traces plot:
        trace_plot_title = 'XAS Traces'
        trace_plot = XYPlot(trace_plot_title, trace_plot_title,
                            [self.bin_edges[1:], self.bin_edges[1:]],
                            [(abs_lon_mp+abs_lon_mm)/2, (abs_loff_mm+abs_loff_mp)/2],
                            xlabel=self.scan_key)
        # Make laser on/laser off difference plots:
        diff_plot_title = 'XMCD Traces'
        diff_plot = XYPlot(diff_plot_title, diff_plot_title,
                           [self.bin_edges[1:], self.bin_edges[1:]],
                           [(abs_lon_mp-abs_lon_mm), (abs_loff_mp-abs_loff_mm)],
                           xlabel=self.scan_key)
        # Make histogram plot of amounts of data collected
        norm_title = 'Normalization signal sums'
        norm_plot = XYPlot(norm_title, norm_title,
                           [self.bin_edges[1:], self.bin_edges[1:], self.bin_edges[1:], self.bin_edges[1:]],
                           [self.lon_hists['norm_mp'], self.lon_hists['norm_mm'], self.loff_hists['signal_mp'], self.loff_hists['signal_mm']],
                           xlabel=self.scan_key)

        # Update plots:
        xmcd_plots.add(trace_plot)
        xmcd_plots.add(diff_plot)
        xmcd_plots.add(norm_plot)
        publish.send('xmcd_plots', xmcd_plots)

