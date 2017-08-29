"""
Functions to simulate MONO zero-order focussing 
"""

import numpy as np
from utils import GaussFit

# Global variables to define how mirror focus varies
width_coeff = [1.0,1.0,1.0]


def width(mirror_pos)  :
    """
    get width of beam as function of mirror-position
    """

    beam_width = np.polyval(width_coeff, mirror_pos)
    print beam_width
    return beam_width


# Global variables to define projection
# ==> projection parameters
mean = 511.0
height = 6000.0
pedestal = 4000.0

# ===> noise parameters
noise = 50.0
#mean_noise = 1.0
#height_noise = 100.0
#pedestal_noise = 10.0
#width_noise = 1.0


def projection(mirror_pos,xvals) :
    """
    Function to emulate projection from EXS_OPAL
    Use a gaussian + noise
    """

    # Create gaussian to simulate projection
    gauss_data = GaussFit.gauss(xvals,
                                mean,
                                width(mirror_pos),
                                height, 
                                pedestal)
                  
    
    # Add noise to data
    gauss_data += np.random.normal(0.0,1.0,len(xvals)) * noise

    return gauss_data


def image(*arg) :
    print "calling zero-order simulation"
    mirror_pos = None
    ncol = None
    nrow = None

    print len(arg), arg

    if len(arg) != 1 :
        mirror_pos = arg[1]
        ncol = arg[2]
        nrow = arg[3]
        
    elif len(arg[0]) != 1 :
        mirror_pos = arg[0][1]
        ncol = arg[0][2]
        nrow = arg[0][3]
        
    elif len(arg[0][0]) != 1:
        mirror_pos = arg[0][0][1]
        ncol = arg[0][0][2]
        nrow = arg[0][0][3]


    print mirror_pos,ncol,nrow

    proj = projection(mirror_pos,np.arange(0.0,ncol))
    return np.tile(proj, (nrow,1))

