"""
Script to calculate the width from Soft X-Ray self-seeding
"""

from sxr_common.epics_camera import epics_camera as epics_camera
from utils import GaussFit
import pyca
import numpy as np
import matplotlib.pyplot as plt


def gaussFit(data) :

    # Create x-axis                                                             
    xaxis = np.arange(data.size)

    # Estimate parameters                                                       
    params_estimate = GaussFit.gauss_params_estimate(data)
    print "Estimate:",params_estimate

    print "Fitting"
    fit_params, fit_cov = GaussFit.curve_fit(GaussFit.gauss, xaxis,data,
                                             params_estimate)
    fit_params_error = np.sqrt(np.diag(fit_cov))


    fit_results = {'mean':fit_params[0],
                   'sigma':fit_params[1],
                   'height':fit_params[2],
                   'pedestal':fit_params[3],
                   'mean_error':fit_params_error[0],
                   'sigma_error':fit_params_error[1],
                   'height_error':fit_params_error[2],
                   'pedestal_error':fit_params_error[3]}

    return fit_results




# Connect to camera
try:
    camera = epics_camera("SXR:EXS:CVV:01")
    camera.connect()
except pyca.pyexc, e:
    print "ERROR: PYCA Error:",e
except pyca.caexc, e:
    print "ERROR: Channel Access Error:",e



# Collect 300 projections
projections_store = camera.collect_h_projections(300)
print projections_store.shape

# Average first 100 to define cuts for self-seeding
self_seeded = np.sum(projections_store[:100],axis=0) / 100.0
print self_seeded.shape

# Now fit --> should pick up largest peak, which should be the
# self-seeded peak
print "Fitting average of first 100 shots"
self_seed_params = gaussFit(self_seeded)
print self_seed_params

xaxis = np.arange(1024)
plt.plot(self_seeded)
plt.plot(GaussFit.gauss(xaxis,
                         self_seed_params['mean'], 
                         self_seed_params['sigma'], 
                         self_seed_params['height'], 
                         self_seed_params['pedestal'])
          )
plt.show()

# Use mean+/-3*sigma to define cut
self_seed_lower_cut = self_seed_params['mean'] - (2.35 * self_seed_params['sigma'])
if self_seed_lower_cut < 0.0 : self_seed_lower_cut = 0.0

self_seed_upper_cut = self_seed_params['mean'] + (2.35 * self_seed_params['sigma'])
if self_seed_upper_cut > 1023.0 : self_seed_upper_cut = 1023.0

print self_seed_lower_cut
print self_seed_upper_cut


# Use self-seeded height to define minimum height to cut off SASE peaks
self_seed_height_cut = 0.5 * self_seed_params['height']


# Use remainder of collect data to select self-seeded peaks, and then
# measure width
seed_width = []
xaxis=np.arange(1024)
for projection in projections_store[100:] :

    projection_fit = gaussFit(projection[self_seed_lower_cut:self_seed_upper_cut])

    plt.plot(projection)
    plt.plot(GaussFit.gauss(xaxis,
                            self_seed_params['mean'], 
                            self_seed_params['sigma'], 
                            self_seed_params['height'], 
                            self_seed_params['pedestal'])
             )
    plt.show() 
        
    if projection_fit['height'] > self_seed_height_cut:
        seed_width.append(2.35 * projection_fit['sigma'])



print seed_width
print np.mean(seed_width)                




