"""
Script to automatically tune the SXR monochromator
This version will attempt to capture individual shots and then process
them. 
"""

from epics_camera import epics_camera
from common.motor import Motor as psmotor
import numpy as np
import pyca
from Pv import Pv
from SpectrometerSharpness.theAlgorithm import main as sharpness
import matplotlib.pyplot as plt
import time

def calculate_sharpness(data) :
    print "Calculate sharpness",
    if data is not None :
        print data.shape
        return sharpness(data)
    else :
        print "no image"
        return -1.0
    



def scan_mirror(mirrorpv, gratingpv, start, finish, stepsize, camerapv):
    
    # Generate mirror positions to step through
    mirrorpos = np.arange(start,finish,stepsize)

    #print camerapv.get_naverage()
    
    # Create empty list that will store sharpness at each mirror position
    sharpness = []
    sharpness_rms = []

    # Step through mirror positions
    for pos in mirrorpos :
        
        # Get initial mirror position
        mirror_initial =   mirrorpv.wm()
        mirrorStep = pos - mirror_initial

        # Move mirror & wait for motion to complete
        mirrorpv.mv(pos)
        
        # move grating to keep image in middle   
        # 1.3 --> for 100 lines/mm grating
        # 1.594 --> for 200 lines/mm grating
        gratingpv.mvr(1.594 * mirrorStep)

        # wait for motion to finish
        mirrorpv.wait()
        gratingpv.wait()

        # CRUCIAL: Wait 1 second for mechanics to stabilize before
        # taking image 
        time.sleep(1)

        # Grab a set of 50 images
        print "Collecting images"
        image_store = camerapv.collect_images(10)
        print "Image store:",image_store.shape

        # Make projection for each image : Will need to fix 
        projection_store = np.sum(image_store,axis=2)        
        print "Projection Store:",projection_store.shape
        
        # Calculate sharpness for each projection
        sharpness_per_image = \
            [calculate_sharpness(projection) \
                 for projection in projection_store]

        # Get avg & standard deviation of  sharpness
        sharpness.append(np.mean( sharpness_per_image ))
        sharpness_rms.append(np.std( sharpness_per_image ))
    
        #plt.figure(10)
        #for projection in projection_store:
        #    plt.plot(projection)
        
        #plt.figure(110)
        #plt.imshow(image_store[0])

        #plt.show()


    # Return data
    print mirrorpos
    print sharpness
    print sharpness_rms
    return (mirrorpos,sharpness,sharpness_rms)



def run_scan() :

     try:
         mirror = psmotor("SXR:MON:MMS:05")
         grating = psmotor("SXR:MON:MMS:06")
         camera = epics_camera("SXR:EXS:CVV:01")
         camera.connect()         

         mirrorpos, sharpness, sharpness_rms = scan_mirror(mirror,grating,
                                                           -0.25,-0.15,0.01,
                                                           camera)          
     except pyca.pyexc, e:
         print "ERROR: PYCA Error:",e
     except pyca.caexc, e:
         print "ERRROR: Channel Access Error:",e

     
     # Close EPICS PV connection
     camera.disconnect()

     return (mirrorpos,sharpness,sharpness_rms)


def plot_data(mirrorpos, sharpness,sharpness_rms, fitted_sharpness):
    plt.figure(1)
    plt.clf()
    plt.title("SXR Spectrometer Sharpness Vs Mirror Position")
    plt.xlabel("Mirror Position")
    plt.ylabel("Spectrometer Sharpness")
    plt.grid(True)
    plt.errorbar(mirrorpos, sharpness, yerr=sharpness_rms,fmt='bo')
    plt.plot(mirrorpos,fitted_sharpness,'r--')
    plt.show()


def fit_data(mirrorpos, sharpness) :
    
    # fit data to 4th order polynomial
    coeff = np.polyfit(mirrorpos, sharpness,4)
    
    # find roots of the gradient --> ie: maxima
    gradient = np.poly1d([4.0 * coeff[0],
                         3.0 * coeff[1],
                         2.0 * coeff[2],
                         coeff[3]])
    roots = gradient.r

    # find root for 2nd derivative
    gradient_2nd = np.poly1d([12.0 * coeff[0],
                             6.0 * coeff[1],
                             2.0 * coeff[2]])
    gradient_2nd_roots = gradient_2nd(roots)

    return np.polyval(coeff, mirrorpos),roots,gradient_2nd_roots


if __name__ == "__main__" :

    time_start = time.time()
    mirrorpos,sharpness,sharpness_rms = run_scan()
    time_taken = time.time() - time_start
    print "Time take for scan:",time_taken

    fitted_sharpness,roots,roots2 = fit_data(mirrorpos,sharpness)
    print "ROOTS:",roots,roots2
    plot_data(mirrorpos, sharpness,sharpness_rms, fitted_sharpness)
    



