"""Class to keep track of, calculate, and plot correlations of two
variables with data being continuously fed in.

Daniel Higley: 2015-06--2016-01
"""

import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

print 'IMPORTING LCLS MODULES...'
from psmon import publish
from psmon.plots import XYPlot, Image, Hist, MultiPlot
print 'DONE'
print 'Starting server'
print 'Setting ZMQ publishing'
publish.init(port=12301, local=True)

class CorrStats:
    """Keep track of, calculate, and plot correlations of two variables
    The variables being correlated are called x and y.
    """
    def __init__(self, x_name='x', y_name='y', plots_name='xvsy',
                 perc_too_high=95, perc_too_low=30):
        # Initialize naming variables
        self.x_name = x_name
        self.y_name = y_name
        self.plots_name = plots_name
        self.perc_too_high = perc_too_high
        self.perc_too_low = perc_too_low
        # Initialize correlation statistics variables:
        self.num_points = 0   # Total number of points recorded
        self.x_sum = 0        # Sum of all the x values
        self.xx_sum = 0       # Sum of all the squared x values
        self.y_sum = 0        # sum of all the y values
        self.yy_sum = 0       # Sum of all the squared y values
        self.xy_sum = 0       # Sum of x times y
        self.yy_div_x_sum = 0 # Sum of y squared divided by x
        self.pearson = 0      # Running Pearson correlation coefficient
        self.snr = 0          # Running signal-to-noise ratio
        self.upd_pearson = 0  # Pearson correlation coefficient after
                              # each plot update
        self.upd_snr = 0      # Signal-to-noise ratio after each plot
                              # update
        self.upd_x_data = np.array([]) # x data from last update
        self.upd_y_data = np.array([]) # y data from last update

    def _linearity_data(self, x, y, num_bins=50):
        """Return data to make a linearity plot out of
        """
        if x is None or y is None or len(x) == 0 or len(y) == 0:
            data = {'x_avgs': np.zeros(num_bins),
                    'y_avgs': np.zeros(num_bins),
                    'fit_coef_lin': (0, 0),
                    'lin_y_vals': np.zeros(num_bins)}
            return data
        # Bin the data
        x_sums, bin_locs = np.histogram(x, bins=num_bins, weights=x)
        y_sums, unused = np.histogram(x, bins=bin_locs, weights=y)
        bin_counts, unused = np.histogram(x, bins=bin_locs)
        x_avgs = x_sums/bin_counts
        y_avgs = y_sums/bin_counts
        # Fit the binned data, ignoring NANs and weighted by the number
        # of data points in each bin
        idx_not_nan = ~np.isnan(y_avgs)
        fit_coef_lin = np.polyfit(x_avgs[idx_not_nan],
                                  y_avgs[idx_not_nan], deg=1,
                                  w=bin_counts[idx_not_nan])
        # Calculate the y values of the linear fit
        lin_y_vals = np.polyval(fit_coef_lin, x_avgs)
        # Return the binned data and its fit
        data = {'x_avgs': x_avgs,
                'y_avgs': y_avgs,
                'fit_coef_lin': fit_coef_lin,
                'lin_y_vals': lin_y_vals}
        return data

    def _calc_pearson(self, num_points, ab_sum, a_sum, aa_sum,
                      b_sum, bb_sum):
        """Return the Pearson correlation coefficient of a and b
        """
        a_avg = a_sum/num_points
        aa_avg = aa_sum/num_points
        a_std = np.sqrt(aa_avg-a_avg**2)
        b_avg = b_sum/num_points
        bb_avg = bb_sum/num_points
        b_std = np.sqrt(bb_avg-b_avg**2)
        ab_avg = ab_sum/num_points
        pearson = (ab_avg-a_avg*b_avg)/(a_std*b_std)
        return pearson

    def _calc_snr(self, a_sum, b_sum, bb_sum, bb_div_a_sum):
        """Calculate the weighted SNR of b/a, weighted by a
        """
        weighted_mean = b_sum/a_sum
        weighted_var = bb_div_a_sum/a_sum-weighted_mean**2
        weighted_std = np.sqrt(weighted_var)
        weighted_snr = weighted_mean/weighted_std
        return weighted_snr

    def _filt_idx(self, datas, perc_too_high=95, perc_too_low=30):
        """Return indicies of data within specified percentages
        """
        too_high = scipy.stats.scoreatpercentile(datas, perc_too_high)
        too_low = scipy.stats.scoreatpercentile(datas, perc_too_low)
        filt_idx = (datas > too_low) & (datas < too_high)
        return filt_idx

    def upd_corr_stats(self, upd_x_data, upd_y_data):
        """Update data and correlation statistics with the input data
        """
        self.upd_x_data = np.copy(upd_x_data)
        self.upd_y_data = np.copy(upd_y_data)
        # for statistics, filter out the lowest and highest points
        filt_idx = self._filt_idx(upd_x_data, self.perc_too_high,
                                  self.perc_too_low)
        x_filt = upd_x_data[filt_idx]
        y_filt = upd_y_data[filt_idx]
        # Calculate update statistics
        upd_num_points = np.size(x_filt)
        upd_x_sum = np.sum(x_filt)
        upd_xx_sum = np.sum(x_filt**2)
        upd_y_sum = np.sum(y_filt)
        upd_yy_sum = np.sum(y_filt**2)
        upd_xy_sum = np.sum(x_filt*y_filt)
        upd_yy_div_x_sum = np.sum(y_filt**2/x_filt)
        self.upd_pearson = self._calc_pearson(upd_num_points, upd_xy_sum,
                                              upd_x_sum, upd_xx_sum,
                                              upd_y_sum, upd_yy_sum)
        self.upd_snr = self._calc_snr(upd_x_sum, upd_y_sum, upd_yy_sum,
                                      upd_yy_div_x_sum)
        # Calculate running statistics
        self.num_points += upd_num_points
        self.x_sum += upd_x_sum
        self.xx_sum += upd_xx_sum
        self.y_sum += upd_y_sum
        self.yy_sum += upd_yy_sum
        self.xy_sum += upd_xy_sum
        self.yy_div_x_sum += upd_yy_div_x_sum
        self.pearson = self._calc_pearson(self.num_points, self.xy_sum,
                                          self.x_sum, self.xx_sum,
                                          self.y_sum, self.yy_sum)
        self.snr = self._calc_snr(self.x_sum, self.y_sum, self.yy_sum,
                                 self.yy_div_x_sum)

    def publish_corr_plots(self):
        """Publish correlation plots between x and y
        """
        # Make MultiPlot to hold correlation plots
        plots_title = ''.join([self.x_name, ' Vs ', self.y_name,
                              ' Correlation Plots'])
        corr_plots = MultiPlot(plots_title, plots_title, ncols=3)
        # Make scatter plot
        scat_plot_title = ''.join([self.y_name, ' Vs ', self.x_name,
                                   ' Scatter Plot'])
        scat_plot_text = ''.join(['Pearson: ',
                                  str(format(self.pearson, '.3f')),
                                  ' Update Pearson: ',
                                  str(format(self.upd_pearson, '.3f')),
                                  '\n SNR: ',
                                  str(format(self.snr, '.3f')),
                                  ' Update SNR: ',
                                  str(format(self.upd_snr, '.3f'))])
        scat_plot = XYPlot(scat_plot_text, scat_plot_title,
                           np.copy(self.upd_x_data), np.copy(self.upd_y_data),
                           xlabel=self.x_name, ylabel=self.y_name,
                           formats='b.')
        # Make linearity plot
        lin_data = self._linearity_data(self.upd_x_data, self.upd_y_data)
        lin_plot_title = ''.join([self.y_name, ' Vs ', self.x_name,
                                  ' Linearity Plot'])
        lin_plot_text = 'Red is Binned Data, Green is Linear Fit'
        lin_plot = XYPlot(lin_plot_text, lin_plot_title,
                          [lin_data['x_avgs'], lin_data['x_avgs']],
                          [lin_data['lin_y_vals'], lin_data['y_avgs']],
                          xlabel=self.x_name, ylabel=self.y_name,
                          formats=['g-', 'r-'])
        # Make histogram plot using filtered data
        filt_idx = self._filt_idx(self.upd_x_data, self.perc_too_high,
                                  self.perc_too_low)
        x_filt = self.upd_x_data[filt_idx]
        y_filt = self.upd_y_data[filt_idx]
        norm_data = y_filt/x_filt
        norm_data = norm_data/np.average(norm_data, weights=x_filt)
        hist_data, hbin_edges = np.histogram(norm_data,
                                             bins=20,
                                             weights=x_filt)
        hbin_centers = (hbin_edges[1:]+hbin_edges[:-1])/2
        hist_plot_title = ''.join([self.y_name, ' Normalized by ',
                                   self.x_name, ' Histogram'])
        hist_plot = Hist('', hist_plot_title,
                         hbin_edges, hist_data)
        # Add created plots to plot list
        corr_plots.add(scat_plot)
        corr_plots.add(lin_plot)
        corr_plots.add(hist_plot)
        publish.send(self.plots_name, corr_plots) 
