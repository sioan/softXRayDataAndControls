"""
Functions to simulate MONO first-order focussing 
"""

import numpy as np
from utils import GaussFit

# Global variables to define how mirror focus varies
# Assume a quadratic form of ax^2 + bx + c
# where width_coeff[a,b,c]
#width_coeff = [0.1,0.1,0.1]
width_coeff = [1.0,1.0,5.0]


def width(mirror_pos)  :
    """
    get width of beam as function of mirror-position
    """    
    return np.polyval(width_coeff, mirror_pos)


# Global variables to define projection
# ==> number of spikes & distance between them
spike_number = 50
spike_height = 6000.0
spike_pedestal = 4000.0

# ===> noise parameters
spike_noise = 50.0


def collect_projections(nimage,mirror_pos,xvals) :
    projection_list = [projection(mirror_pos,xvals) for i in range(nimage)]
    return projection_list



def projection(mirror_pos,xvals) :
    """
    Function to emulate projection from EXS_OPAL when mono is in first order
    Simulate FEL spectrum as sum of Gaussians spread over CCD, whose
    width is dictated by the mirror position, with random mean and height.
    Number of gaussians is also random
    """

    # get length of xvals
    len_xvals = len(xvals)

    # Generate random number of spikes
    n_spikes = int(spike_number * ((np.random.random(1) * 2.0 )-1.0) * 0.1) \
        + (spike_number/2.0)


    # Create random position of the spikes of length n_spikes
    mean_list = np.random.random(n_spikes) * len_xvals
    
    
    # Create random heights of the spikes
    height_list = np.random.random(n_spikes) * spike_height
    

    sim_projection = np.zeros(len_xvals)
    
    for mean, height in zip(mean_list,height_list) :
        sim_projection += (GaussFit.gauss(xvals,
                                          mean,
                                          width(mirror_pos),
                                          height,
                                          spike_pedestal))
        
    # Add noise
    sim_projection += np.random.normal(0.0,1.0,len_xvals) * spike_noise

    return sim_projection


if __name__ == "__main__" :
    import numpy as np
    import matplotlib.pyplot as plt
    from utils.SpectrometerSharpness.theAlgorithm import main as sharpness
    

    #spike_pedestal = 0.0
    
    xvals = np.arange(0.0,100)

    import sys
    spectrum = projection(-0.5,xvals)
    derivative = spectrum[1:] - spectrum[:-1]


    #sys.exit()


    mirror_pos = np.arange(-10.0,10.0,0.5) 





    avg_sharpness = []
    std_sharpness = []
    for m in mirror_pos :
        theSharpness = []
        for i in range(10) :
            spectrum = projection(m,xvals)
            theSharpness.append(sharpness(spectrum))
            
        avg_sharpness.append(np.mean(theSharpness))
        std_sharpness.append(np.std(theSharpness))


    # Fit gaussian to avg_sharpness
    fit_params = GaussFit.GaussFit(np.array(avg_sharpness), mirror_pos)
    print fit_params

    fit_plot = GaussFit.gauss(mirror_pos, 
                              mean=fit_params['mean'],
                              sigma=fit_params['sigma'],
                              height=fit_params['height'],
                              pedestal=fit_params['pedestal'])
    

    
    
    

    





    
    #plt.clf()
    #plt.plot(spectrum)
    #plt.draw()


    #print proj_list

    #plt.clf()
    #plt.plot(proj_list)
    #for spike in proj_list :
    #    plt.plot(spike)
    #plt.show()
