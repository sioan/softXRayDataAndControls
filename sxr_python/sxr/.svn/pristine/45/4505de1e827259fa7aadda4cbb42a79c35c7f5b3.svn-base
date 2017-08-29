"""
GaussFitTest

PYTHON script to test fitting gaussians in PYTHON
---> SHOULD PUT THIS IN PYPSALG

"""

import numpy as np
import scipy 
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# ---> SHOULD BE IN PYPSALGO
def gauss(x, mean, sigma, height=1.0, pedestal=0.0) :
    return  (height * np.exp(-0.5 * ((x-mean)/sigma)**2)) + pedestal



def create_test_gaussian(x,noise_amplitude=1.0) :

    # create a gaussian for testing fiting routine
    mean     = np.random.random() * 511.0
    sigma    = np.random.random() * 5.0
    height   = np.random.random() * 100.0
    pedestal = np.random.random() * 10.0

    gauss_data = gauss(x,mean,sigma,height,pedestal) + \
        (np.random.normal(0.0,1.0,512)*noise_amplitude)

    return gauss_data,mean,sigma,height,pedestal


# ---> SHOULD BE IN PYPSALGO
def FWHM(data) :
    """
    Start from tallest bin and then go up in increasing x until bin
    content is half.  Then repeat in oppostite direction.  Take the
    average of the two as measure of FWHM.
    
    """

    # Find peak value and its index
    peakIndex = np.argmax(data)
    peakValue = data[peakIndex]
    
    # Use mean of lowest 10% of data to estimate pedestal
    lowestTenPercent = int(0.1 * data.size)
    lowestValue = np.sort(data)[:lowestTenPercent]
    pedestal = np.mean(lowestValue)

    # Value of height
    height = peakValue - pedestal
    
    # Split array to values before and after peak
    # --> lowerHalf array is reversed, so index is distance from peak
    lowerHalf = (data[:peakIndex])[::-1]
    upperHalf = data[peakIndex:]
    
    # Lower half FWHM
    #- Find largest index that is <= height/2.0 +pedestal
    lowerFWHMIndex = np.argwhere(lowerHalf <= (height/2.0 + pedestal)).flatten()
    lowerFWHM = lowerFWHMIndex[0] if lowerFWHMIndex.size>0 else None
    
    # Upper half FWHM
    #- Find smallest index that is <= height/2.0 +pedestal
    upperFWHMIndex = np.argwhere(upperHalf <= (height/2.0 + pedestal)).flatten()
    upperFWHM = upperFWHMIndex[0] if upperFWHMIndex.size>0 else None
        
    # Calculate FWHM, taking into account if lower or upper FWHM were
    # contained within data
    fwhm = None

    # - no upper or lower FWHM found ==> take entire width as estimate
    if (lowerFWHM is None) and (upperFWHM is None) :
        fwhm = data.size
    
    # - Only lower FWHM was found
    if (lowerFWHM is not None) and (upperFWHM is None) :
        fwhm = lowerFWHM

    # - Only upper FWHM was found
    if (lowerFWHM is None) and (upperFWHM is not None) :
        fwhm = upperFWHM

    # - Lower and Upper FWHM found - take average of the two
    if (lowerFWHM is not None) and (upperFWHM is not None) :
        fwhm = (lowerFWHM + upperFWHM) / 2.0

    return fwhm



def gauss_params_estimate(data,xaxis=None) :
    """
    Estimate of gaussian parameters without fitting
    """
    # Use index of largest value in data to estimate mean
    mean = np.argmax(data)
    
    # Use mean of lowest 10% of data to estimate pedestal
    lowestTenPercent = int(0.1 * data.size)   
    lowestValue = np.sort(data)[:lowestTenPercent]
    pedestal = np.mean(lowestValue)
    
    # Use difference of largest value in data and pedestal to estimate
    # height
    height = data[mean] - pedestal
    
    # Estimate sigma from FWHM, which is 2.36*sigma
    sigma = FWHM(data) / 2.36

    if xaxis is not None:
        mean = xaxis[mean]
        sigma *= np.abs(xaxis[1]-xaxis[0])

    return mean,sigma,height,pedestal

 

def GaussFit(data,xaxis=None) :
    """
    General interface to fit data to gaussian
    """

    if xaxis is None:
        # use array index of data to define x-axis
        xaxis = np.arange(data.size)

    params_estimate = gauss_params_estimate(data,xaxis)

    try: 
        fit_params, fit_cov = curve_fit(gauss,xaxis,data,params_estimate)
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
    except RuntimeError:
        print "Fit failed to converge - using estimates"
        fit_results = {'mean':params_estimate[0],
                       'sigma':params_estimate[1],
                       'height':params_estimate[2],
                       'pedestal':params_estimate[3],
                       'mean_error':np.nan,
                       'sigma_error':np.nan,
                       'height_error':np.nan,
                       'pedestal_error':np.nan}
        return fit_results
    except ValueError:
        print "Data contains NAN"
    except :
        print "Uknown error"
                   
    
    


if __name__ == "__main__" :

    xaxis = np.arange(512)
    noise_amplitude = 1.0

    params = np.empty(4)
    data,params[0],params[1],params[2],params[3] \
        = create_test_gaussian(xaxis,noise_amplitude)

    realgauss = gauss(xaxis, *params)
    
    params_estimate = gauss_params_estimate(data)
    crude_fit = gauss(xaxis,*params_estimate)
        
    print "Initial:",params
    print "Estimate:",params_estimate

    print "Fitting"
    fit_params, fit_cov = curve_fit(gauss,xaxis,data,params_estimate)
    fit_params_error = np.sqrt(np.diag(fit_cov))

    print "Final Fit(errors):",zip(fit_params,fit_params_error)
    print "Covariance Matrix:",fit_cov
    gauss_fit = gauss(xaxis, *fit_params)    

    print "Parameter \t Fit \t Error \t Diff \t Status"
    for p,fit,fit_error in zip(params,fit_params,fit_params_error) :
        diff = abs(p-fit)
        fitStatus = "GOOD" if diff < fit_error else "BAD"
        print p,"\t",fit,"\t",fit_error,"\t",diff,"\t",fitStatus
        
    print "Plotting"    
    plt.figure(1)
    plt.clf()
    plt.plot(data,'.', realgauss,'p',crude_fit,'.',gauss_fit,'-')
    plt.draw()
    plt.show()
    
