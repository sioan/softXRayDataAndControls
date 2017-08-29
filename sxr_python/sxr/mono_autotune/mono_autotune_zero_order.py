"""
Script to automatically tune the SXR monochromator
This version will attempt to capture individual shots and then process
them. 
"""

from sxr_common.epics_camera import epics_camera as epics_camera
from sxr_common.epics_gasdet import epics_gasdet as epics_gasdet 
from common.motor import Motor as psmotor
from common.pypsElog import pypsElog as elog

from utils import GaussFit

import numpy as np
import pyca
from Pv import Pv
from utils.SpectrometerSharpness.theAlgorithm import main as sharpness
import matplotlib.pyplot as plt
import time
import tempfile
import shutil


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

    #print "Final Fit(errors):",zip(fit_params,fit_params_error)
    #print "Covariance Matrix:",fit_cov

    combinedvals = zip(fit_params,fit_params_error)
    print "Fit Values(errors):"
    print "mean:",combinedvals[0],
    print "sigma:",combinedvals[1],
    print "Height:",combinedvals[2],
    print "Pedestal:",combinedvals[3]

    return fit_params,fit_params_error



    



def calculate_sharpness(data) :
#    print "Calculate sharpness",
    if data is not None :
#        print data.shape
        return sharpness(data)
    else :
#        print "no image"
        return -1.0
    

def mirror_to_grating_factor(gratingrule, photonE) :
        # move grating to keep image in middle   
        # 1.0 --> for zero-order grating
        # 1.3 --> for 100 lines/mm grating
        # 1.594 --> for 200 lines/mm grating

        # ==> Parameterised fit, courtesy of Daniel Cocco
        #Cf(100l/mm)=2.7183-0.0034357*E+0.0000029749*E^2-0.0000000009418*E^3
        #Cf(200 l/mm)=3.791-0.0045848*E+0.0000033009*E^2-0.00000000087928*E^3
        
        factor = 0.0
        
        if (gratingrule == 0) :
            factor = 1.0 
        if (gratingrule == 100) :
            factor = np.polyval([-0.0000000009418,+0.0000029749,-0.0034357,2.7183],
                                 photonE)
        if (gratingrule == 200) :
            factor =np.polyval([-0.00000000087928,+0.0000033009,-0.0045848,3.791],
                                photonE)

        return factor



def get_averaged_image(gasdetpv,camerapv,naverage=200) :
    # Collect 200 images and return average, while checking shots are
    # not dropped. If there are dropped shots during collection,
    # repeat collection.  If after 10 attempts, still get dropped
    # shots, raise error 

    n_attempts = 0
 
    # Create store for all projections
    projection_store = None

    for n_attempts in range(10) :
                
        # Start counting dropped shots
        gasdetpv.start_dropshot_counting(threshold=0.0)

        # collect projections
        #projection_store = camerapv.collect_h_projections(nprojections)
        #print "Projection Store:",projection_store.shape
      
        # Get averaged image
        image = camerapv.avg_image(naverage=naverage)

        # Stop counting dropped shots
        gasdetpv.stop_dropshot_counting()

        # break out for loop if no shots dropped
        if (gasdetpv.dropped_shots() == 0) :
            break
        else :
            print "FEL dropped shot. trying again"


    if (n_attempts == 9) :
        print "After 10 attempts, failed to collect projections"
        print "without FEL dropping a shot. Stopping auto-tuning"
        print "Check with MCC about status of FEL"
        raise
    

    return image
 




def scan_mirror(mirrorpv, gratingpv, begin, end, stepsize, camerapv,gasdetpv,
                gratingrule,photonE):
    
    # Generate mirror positions to step through
    mirrorpos = np.arange(begin,end,stepsize)

    # Create empty array of same shape that will log grating position
    #gratingpos = np.zeros(mirrorpos.shape)
    gratingpos = []
            
    # Create empty list that will store fwhm at each mirror position
    fwhm = []
    fwhm_rms = []

    # Step through mirror positions
    for pos in mirrorpos :

        print "Move Mirror:",pos
        
        # Get initial mirror position
        mirror_initial =   mirrorpv.wm()
        mirrorStep = pos - mirror_initial

        # Move mirror & wait for motion to complete
        mirrorpv.mv(pos)
        
        # move grating to keep image in middle   
        # 1.0 --> for zero-order grating
        # 1.3 --> for 100 lines/mm grating
        # 1.594 --> for 200 lines/mm grating
        #if (gratingrule == 0) :
        #    gratingpv.mvr(1.0 * mirrorStep)
        #if (gratingrule == 100) :
        #    gratingpv.mvr(1.58 * mirrorStep)
        #if (gratingrule == 200) :
        #    gratingpv.mvr(1.594 * mirrorStep)
        gratingpv.mvr(mirror_to_grating_factor(gratingrule, photonE) * mirrorStep)
        

        # wait for motion to finish
        mirrorpv.wait()
        gratingpv.wait()

        # CRUCIAL: Wait 1 second for mechanics to stabilize before
        # taking image 
        time.sleep(1)

        # log grating position
        gratingpos.append(gratingpv.wm())

        # Get averaged image
        image =  get_averaged_image(gasdetpv,camerapv) 
        
        # Do projection
        image_projection = np.sum(image, axis=0)

        # Fit Gaussian 
        fit_params,fit_params_error = gaussFit(image_projection)
        

        # Collect 200 horizontal projections
        #projection_store = collect_projections(gasdetpv,camerapv)
        #print "Projection Store:",projection_store.shape
        
        # Calculate sharpness for each projection
        #sharpness_per_image = \
        #    [calculate_sharpness(projection) \
        #         for projection in projection_store]

        # Store FWHM (converted from sigma) and error
        fwhm.append(fit_params[1] * 2.35)
        fwhm_rms.append(fit_params_error[1] * 2.35)
    
        #xaxis = np.arange(image_projection.size)
        #gauss_data = GaussFit.gauss(xaxis,*fit_params)

        #plt.figure(10)
        #plt.plot(image_projection,"o")        
        #plt.plot(gauss_data,"-")        
        #plt.show()




    # Return data
    #print mirrorpos
    #print gratingpos
    #print sharpness
    #print sharpness_rms
    return (mirrorpos,gratingpos,fwhm,fwhm_rms)



def run_scan(begin,end,stepsize,gratingrule,photonE,
             camera_pv="SXR:EXS:CVV:01",
             mirror_pv="SXR:MON:MMS:05",
             grating_pv="SXR:MON:MMS:06",
             gasdet_pv="GDET:FEE1:241"):
    
    raw_input("Please center spectrum [press enter when done]")
    
    # Create the camera and gasdet variables
    camera = None
    gasdet = None
    mirrorpos = None
    gratingpos = None
    fwhm = None
    fwhm_rms = None
    fitted_fwhm = None

    try :         
        mirror = psmotor(mirror_pv)
        grating = psmotor(grating_pv)
        
        camera = epics_camera(camera_pv)
        #camera.connect()         

        gasdet = epics_gasdet(gasdet_pv)
        gasdet.connect()
        
        mirrorpos, gratingpos, fwhm, fwhm_rms = \
            scan_mirror(mirror,grating,begin,end,stepsize,camera,gasdet,
                        gratingrule,photonE) 
        
    except pyca.pyexc, e:
        print "ERROR: PYCA Error:",e
    except pyca.caexc, e:
        print "ERRROR: Channel Access Error:",e
        
        
    # Close EPICS PV connection
    if camera is not None :
        camera.disconnect()
    if gasdet is not None:
        gasdet.disconnect()
        
    return (mirrorpos,gratingpos,fwhm,fwhm_rms)
    

def plot_data(mirrorpos, fwhm,fwhm_rms, fitted_fwhm):
    plt.figure(1)
    plt.clf()
    plt.title("SXR Spectrometer FWHM Vs Mirror Position")
    plt.xlabel("Mirror Position")
    plt.ylabel("Spectrometer FWHM")
    plt.grid(True)
    plt.errorbar(mirrorpos, fwhm, yerr=fwhm_rms,fmt='bo')
    plt.plot(mirrorpos,fitted_fwhm,'r--')
    plt.show()
    
    return 1


def fit_data(mirrorpos, fwhm, fitfunc) :
    
    optimalMirror,fittedFwhm = fitfunc(mirrorpos,fwhm)
    
    return optimalMirror,fittedFwhm
    


def fit_gauss(mirrorpos, fwhm):
    """
    Fit mirror position vs fwhm to a Gaussian to find optimal
    mirror position
    """
    
    # Estimate parameters
    params_estimate = GaussFit.gauss_params_estimate(fwhm)
    
    # Translate mean and sigma from array index units to mirror
    # position units 
    gradient = (mirrorpos[-1] - mirrorpos[0]) / float(mirrorpos.size)
    params_estimate[0] = mirrorpos[0] + (params_estimate[0] * gradient)
    params_estimate[1] = params_estimate[1] * gradient

    # Fit to Gaussian
    fit_params, fit_cov = GaussFit.curve_fit(GaussFit.gauss,
                                             mirrorpos,fwhm,
                                             params_estimate)
    fit_params_error = np.sqrt(np.diag(fit_cov))

    

    # Return the fitted mean position
    return fit_params[0],GaussFit.gaus(mirrorpos,*fit_params)



def fit_poly2(mirrorpos,fwhm) :
    """
    Fit mirror position vs fwhm to quadaratic to find optimal
    mirror position
    """

    # Fit data to quadratic
    coeff = np.polyfit(mirrorpos, fwhm, 2)

    # Find zero gradiant
    optimalPos = -coeff[1] / (2.0 * coeff[0])

    # Check this is a minima
    if (coeff[0] < 0.0) :
        print "FOUND A MAXIMA RATHER THAN MINIMA !!"
        
    return optimalPos,np.polyval(coeff,mirrorpos)



def fit_poly4(mirrorpos,fwhm) :
    """
    Fit mirror position vs fwhm to 4-th order polynomial to find
    optimal mirror position
    """

    # fit data to 4th order polynomial
    coeff = np.polyfit(mirrorpos, fwhm,4)
    
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

    
    # find solution with negative 2nd derivative root (ie: maxima)
    maxima = roots[gradient_2nd_roots < 0.0]

    if (maxima.size != 1) :
        print "MORE THAN ONE SOLUTION FOUND !!!"
        print "\t ",maxima
        print "WILL BE USING FIRST SOLUTION",maxima[0]
        
    return maxima[0],np.polyval(coeff,mirrorpos)
   #return np.polyval(coeff, mirrorpos),roots,gradient_2nd_roots



def find_grating_from_mirrorpos(mirrorpos, gratingpos,
                                optimalmirrorpos) :
    
    gradient = \
        (gratingpos[-1]-gratingpos[0]) / (mirrorpos[-1]-mirrorpos[0])

    delta_mirrorpos = optimalmirrorpos - mirrorpos[0]
    optimal_grating = gratingpos[0] + (gradient * delta_mirrorpos)
    
    return optimal_grating



def move_mono_to_optimal(optimalMirrorPos, optimalGratingPos,
                         mirror_pv="SXR:MON:MMS:05",
                         grating_pv="SXR:MON:MMS:06") :
    """
    Ask before moving mono to optmial mirror/grating positions
    """
    
    response = \
        raw_input("Move MONO to optimal position? [press 'Y' to accept] ")

    if (response.lower() == 'y') :
        mirror = psmotor(mirror_pv)
        grating = psmotor(grating_pv)
        
        mirror.mv(optimalMirrorPos)
        grating.mv(optimalGratingPos)

        mirror.wait()
        grating.wait()
    
    

def format_results(mirrorpos, gratingpos, fwhm, 
                   optimalmirror, optimalgrating):
    """
    Format collected data into nice formatted string
    """
    
    tableString =  "Mirror \t Grating \t FWHM \n"
    tableString += "------ \t ------- \t --------- \n"
    
    for line in range(mirrorpos.size):
        tableString += "%0.3f \t %0.3f \t %0.3f \n"%(mirrorpos[line],
                                                     gratingpos[line],
                                                     fwhm[line])        
    tableString += "\n"
    tableString += "Optimal Mirror Position: %0.3f \n"%(optimalmirror)
    tableString += "Optimal Grating Position: %0.3f \n"%(optimalgrating)

    return tableString




if __name__ == "__main__" :
    
    plt.ion()

    #mono_mirror  = "SXR:EXP:MMS:31"
    #mono_grating = "SXR:EXP:MMS:32"
    
    mono_mirror  = "SXR:MON:MMS:05"
    mono_grating = "SXR:MON:MMS:06"
    exs_camera = "SXR:EXS:CVV:01"
    fee_gasdet = "GDET:FEE1:241"
    
    print("Enter MONO tuning scan range")
    scan_begin = float(raw_input("Enter MONO mirror start position:"))
    scan_end =  float(raw_input("Enter MONO mirror end position:"))
    scan_stepsize = float(raw_input("Enter MONO mirror step size:"))
    gratingrule = 0
    photonE = 0


    time_start = time.time()
    mirrorpos,gratingpos,fwhm,fwhm_rms = \
        run_scan(begin=scan_begin,
                 end=scan_end,
                 stepsize=scan_stepsize,
                 gratingrule=gratingrule,
                 photonE=photonE,
                 camera_pv=exs_camera,
                 mirror_pv=mono_mirror,
                 grating_pv=mono_grating,
                 gasdet_pv=fee_gasdet)
        
    time_taken = time.time() - time_start
    print "Time take for scan (sec):",time_taken
    
    optimalMirrorPosition,fitted_fwhm = fit_data(mirrorpos,fwhm,
                                                      fit_poly2)
    optimalGratingPosition = find_grating_from_mirrorpos(mirrorpos, 
                                                         gratingpos,
                                                         optimalMirrorPosition
                                                         )
    fignum = plot_data(mirrorpos, fwhm,fwhm_rms, fitted_fwhm)
    scanresults =  format_results(mirrorpos, gratingpos, fwhm, 
                                  optimalMirrorPosition, 
                                  optimalGratingPosition)
    print scanresults
    #    print "Optimal Mirror Position",optimalMirrorPosition
    #    print "Optimal Grating Position", optimalGratingPosition
    move_mono_to_optimal(optimalMirrorPosition,
                         optimalGratingPosition,
                         mono_mirror,mono_grating)    

    postToElog = raw_input("Post results to elog? [press 'Y' to post]")
    if (postToElog.lower() == 'y'):     

        # Save scan plot in a temporary area
        tempDirName = tempfile.mkdtemp()        
        plt.figure(fignum)
        pltfilename = tempDirName + "/mono_scan_results.png"
        plt.savefig(pltfilename)

        # Post results and plot to elog
        sxrelog = elog()
        sxrelog.submit(scanresults,file=pltfilename)

        # Clean up temp area
        shutil.rmtree(tempDirName)


    print "FINISHED"
    

    
    

    



