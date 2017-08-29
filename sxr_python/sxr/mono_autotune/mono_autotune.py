"""
Script to automatically tune the SXR monochromator
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
    print "Calculate sharpness"
    if data is not None :
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
    
    # Step through mirror positions
    for pos in mirrorpos :

        # Get initial mirror position
        mirror_initial =   mirrorpv.wm()
        mirrorStep = pos - mirror_initial

        # Move mirror & wait for motion to complete
        mirrorpv.mv(pos)

        # move grating to keep image in middle
        # 1.3 --> for 100 lines/mm grating
        # xx  --> for 200 lines/mm grating
        gratingpv.mvr(1.594 * mirrorStep)

        # wait for motion to finish
        mirrorpv.wait()
        gratingpv.wait()

        # CRUCIAL: Wait 1 second for mechanics to stabilize before
        # taking image 
        time.sleep(1)

        # Grab averaged image
        image = camerapv.avg_image(naverage=200.0)

        # Do projection 
        projection = np.sum(image,axis=1)    
        #projection_0 = np.sum(image,axis=0)
        
        # Get sharpness
        sharpness.append( calculate_sharpness(projection) )
        
        plt.figure(10)
        plt.plot(projection)        
        
        #plt.figure(20)
        #plt.plot(projection_0)

        plt.figure(110)
        plt.imshow(image)
        plt.show()



    
    # Return data
    print mirrorpos
    print sharpness
    return (mirrorpos,sharpness)



def run_scan() :

     try:
         mirror = psmotor("SXR:MON:MMS:05")    
         grating = psmotor("SXR:MON:MMS:06")
         camera = epics_camera("SXR:EXS:CVV:01")
         camera.connect()         

         mirrorpos, sharpness = scan_mirror(mirror,grating,-0.30,-0.05,0.02,
                                            camera)          
     except pyca.pyexc, e:
         print "ERROR: PYCA Error:",e
     except pyca.caexc, e:
         print "ERRROR: Channel Access Error:",e

     
     # Close EPICS PV connection
     camera.disconnect()

     return (mirrorpos,sharpness)


def plot_data(mirrorpos, sharpness,fitted_sharpness):
    plt.figure(1)
    plt.clf()
    plt.title("SXR Spectrometer Sharpness Vs Mirror Position")
    plt.xlabel("Mirror Position")
    plt.ylabel("Spectrometer Sharpness")
    plt.grid(True)
    plt.plot(mirrorpos,sharpness,'bo',mirrorpos,fitted_sharpness,'r--')
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
    mirrorpos,sharpness = run_scan()
    fitted_sharpness,roots,roots2 = fit_data(mirrorpos,sharpness)
    print "ROOTS:",roots,roots2
    plot_data(mirrorpos, sharpness,fitted_sharpness)
    



