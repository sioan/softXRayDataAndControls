#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:35 2017

@author: elsabreu
"""

import extractorTester
import numpy as np
import matplotlib.pyplot as plt
import h5py
import os
from copy import deepcopy
from scipy.optimize import curve_fit
from scipy import stats as st
from matplotlib import gridspec
import RIXS_funcs

os.chdir('/reg/d/psdm/sxr/sxrlp2615/results/AnalysisLCLS')


def simpleRIXSPlot(runnum,labelStr,thresholdOn=1,errorflag=0):
    [RIXSSumm, ImSumm, I0Vec, I0Summ, MonoPV, ttoolVec]=RIXS_funcs.hdf5AndFile_read(runnum)
    if thresholdOn == 0:
        if(errorflag==1):
            error = AssignError(RIXSSumm)
            plt.errorbar(energyCalib(),RIXSSumm,xerr = None,yerr=error,fmt='--o', label=labelStr)
        else:    
            plt.plot(energyCalib(),RIXSSumm, label=labelStr)
    elif thresholdOn == 1:
        threshold = np.mean(ImSumm)
        RIXSSumm, ImSumm, dummy = thresholdCheck(threshold, ImSumm)
        if(errorflag==1):
            error = AssignError(RIXSSumm)
            plt.errorbar(energyCalib(),RIXSSumm,xerr = None,yerr=error,fmt='--o', label=labelStr)
        else:    
            plt.plot(energyCalib(),RIXSSumm, label=labelStr)
    
        
    plt.xlabel('Energy (eV)')
    plt.ylabel('RIXS Intensity')
    plt.legend(loc=2)
    

def averageRuns(runnums,thresholdOn=1):
    RIXSSumm_sum = np.zeros(512)
    for i in runnums:
        [RIXSSumm, ImSumm, I0Vec, I0Summ, MonoPV, ttoolVec]=RIXS_funcs.hdf5AndFile_read(i)
        if thresholdOn==1:
            threshold = np.mean(ImSumm)
            RIXSSumm, ImSumm, dummy = thresholdCheck(threshold, ImSumm)
        RIXSSumm_sum += RIXSSumm
        
    RIXSSumm_sum = RIXSSumm_sum/len(runnums)    
    return RIXSSumm_sum    
    

# Simple data plotting
def simplePlot(runnum,errorflag=0):# takes runnum as as argument
    # Simple plot
    # runnum = 4
    #[RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec, ttoolVec]=RIXS_funcs.hdf5_read(runnum)
    #[RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec, ttoolVec]=RIXS_funcs.hdf5AndFile_read(runnum)
    [RIXSSumm, ImSumm, I0Vec, I0Summ, MonoPV, ttoolVec]=RIXS_funcs.hdf5AndFile_read(runnum)
    
    plt.figure(101,figsize=(15, 10))
    
    # Full image, to check curvature
    plt.subplot(3,1,1)
    plt.imshow(ImSumm, vmin=np.min(ImSumm), vmax=np.max(ImSumm)/10)
    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
#    plt.xlim([0,2014])
#    plt.ylim([0,512])
    plt.show()
    
    # RIXS spectrum
    plt.subplot(3,1,2)
    if(errorflag==1):
        xx = np.arange(512)
        error = AssignError(RIXSSumm)
        plt.errorbar(xx,RIXSSumm,xerr = None,yerr=error,fmt='--o')
    else:    
        plt.plot(RIXSSumm)
    
    plt.xlabel('Pixels')
    plt.ylabel('RIXS intensity')
    plt.xlim([0,512])
    plt.show()
    
    # With calibrated energy axis
    plt.subplot(3,1,3)
    plt.plot(energyCalib(),RIXSSumm)
    plt.xlabel('Energy (eV)')
    plt.ylabel('RIXS intensity')
    plt.xlim([min(energyCalib()), max(energyCalib())])
    plt.show()

def simplePlot_OLD(runnum):# takes runnum as as argument
    # Simple plot
    # runnum = 4
    #[RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec, ttoolVec]=RIXS_funcs.hdf5_read(runnum)
    #[RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec, ttoolVec]=RIXS_funcs.hdf5AndFile_read(runnum)
    [RIXSSumm, ImSumm, I0Vec, I0Summ, MonoPV, ttoolVec]=RIXS_funcs.hdf5AndFile_read(runnum)
    
    plt.figure(101,figsize=(15, 10))
    
    # Full image, to check curvature
    plt.subplot(3,1,1)
    plt.imshow(ImSumm, vmin=np.min(ImSumm), vmax=np.max(ImSumm)/10)
    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
#    plt.xlim([0,2014])
#    plt.ylim([0,512])
    plt.show()
    
    # RIXS spectrum
    plt.subplot(3,1,2)
    plt.plot(RIXSSumm)
    plt.xlabel('Pixels')
    plt.ylabel('RIXS intensity')
    plt.xlim([0,512])
    plt.show()
    
    # With calibrated energy axis
    plt.subplot(3,1,3)
    plt.plot(energyCalib(),RIXSSumm)
    plt.xlabel('Energy (eV)')
    plt.ylabel('RIXS intensity')
    plt.xlim([min(energyCalib()), max(energyCalib())])
    plt.show()


# Curvature correction
def toCorrectCurvatureAndProject(runnum):
    [RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec, ttoolVec]=RIXS_funcs.hdf5AndFile_read(runnum)
    lenx = 512
    leny = 2048
    x = np.arange(0,lenx,1)
    shit = 200
    mat = ImSumm
        ### FIT THE ELASTIC LINE ###
    
    FittedCenters = np.zeros(leny)
    FittedSigmas = np.zeros(leny)
    FittedAmps = np.zeros(leny)
    
        # do fit with leastsq model
    for i in range(shit/2,leny-shit/2):
        #DataToFit = mat[:,i]
        DataToFit = np.mean(mat[:,i-shit/2:i+shit/2],1)
        #results = RIXS_funcs.NormalFit(x,DataToFit)    
        FittedCenters[i] = np.argmax(DataToFit)
        #FittedCenters[i] = results[0]
        #FittedSigmas[i] = results[2]
        #FittedAmps[i] = results[1]
    
        # RECAST DATA TO HAVE ELASTIC IN A STRAIGHT LINE
    D = np.zeros(leny)
    Ref = round(FittedCenters[shit/2+1])
    matnew = deepcopy(mat)
    #i = 100
    for i in range(shit/2,leny-shit/2):
        D[i] = round(FittedCenters[i]-Ref)
        line = matnew[:,i]     
        matnew[:,i] = np.roll(line,int(-D[i]))
    
    RIXSSumm_corr = np.sum(matnew,axis=1) #Out RIXS data after curvature
    
        #Plotting output
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharey='row')
    ax1.imshow(mat)
    ax1.set_title('Raw Image Data')
    ax2.invert_yaxis()
    ax2.plot(RIXSSumm,x)
    ax2.set_title('Integrated Raw Image')
    ax3.imshow(matnew)
    ax3.set_title('Processed Image Data')
    ax4.invert_yaxis()
    ax4.plot(RIXSSumm_corr,x)
    ax4.plot(RIXSSumm,x)
    ax4.set_title('Integrated Processed Image')
    
    
    return

    #return RIXSSumm_corr


# Energy Calibration
def energyCalib(): # any arguments?
    lenx = 512
    Ka_pix = 253
    Kb_pix = 160
    xData_En = RIXS_funcs.CalibrateEnergy(1011.7*0.5,1034.7*0.5,Ka_pix,Kb_pix,lenx) #Energies and position of two reference peaks, length of data
    return xData_En


# Fancy plot .... to be checked!!
def plotAll(runnums,normflag=0,calibflag=0,errorflag=0,secondnorm=0): #normflag = 1 (normtoArea), normflag = 2 (normtoI0)    
    gs = gridspec.GridSpec(3, 2, width_ratios=[2, 1]) 
    #runnums=np.arange(run_first,run_last+1)
    
    legvec = []
    
    errors=[]
    
    for i in runnums:
        #plt.figure(i)
        #[RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec, ttoolVec]=RIXS_funcs.hdf5_read(i)
        [RIXSSumm, ImSumm, I0Vec, I0Summ, MonoPV, ttoolVec]=RIXS_funcs.hdf5AndFile_read(i)
        #[RIXSSumm, ImSumm, I0Vec, I0Summ, photonEnVec]=RIXS_funcs.hdf5AndFile_read(i)
        
        if normflag == 0: #normflag = 0 (Non norm)
            a = 0
            error = AssignError(RIXSSumm)
        elif normflag==1: #normflag = 1 (NormtoArea)
            RIXSSumm = (RIXSSumm-RIXSSumm[0])/np.sum(RIXSSumm-RIXSSumm[0])
            error = AssignError(RIXSSumm)
        elif normflag==2:#normflag = 1 (NormtoI0)
            RIXSSumm = RIXSSumm/I0Summ
            if(secondnorm==1):
                RIXSSumm = (RIXSSumm-RIXSSumm[0])
            error = AssignError(RIXSSumm)
        else:
            print "The flag must be either 0,1 or 2"
        
        #print I0Summ
        
        en_range = np.arange(512)
        xlabelstr = 'Pixels'
        if calibflag == 1:
            xlabelstr = 'Energy (eV)'
            en_range=energyCalib()    
        
        monoLambda = 3.37585 - 0.573217*MonoPV - 0.0148033*MonoPV**2
        monoEn = 4.14e-15 * 3e8 / (monoLambda*1e-9)
        
#        photonEnVec=photonEnVec[~np.isnan(photonEnVec)]
#        IOVec=IOVec[~np.isnan(IOVec)]
        plt.figure(1,figsize=(15, 10))
        
#       RIXSSumm = toCorrectCurvatureAndProject(ImSumm)# with curvature correction!
        #print I0Summ
        plt.subplot(gs[:,0])
        if(errorflag==1):
            plt.errorbar(en_range,RIXSSumm,xerr=None,yerr=error,fmt='--o')
        else:    
            plt.plot(en_range,RIXSSumm,'-o',label=str(i))
#        plt.plot(RIXSNorm,'-o')
        plt.xlim([min(en_range), max(en_range)])
        plt.ylabel('Spectrum')
        plt.xlabel(xlabelstr)
        
        plt.subplot(gs[0,1])
        plt.hist(ttoolVec,400,histtype='stepfilled')
        #plt.xlim([-0.05,0.05])
        plt.ylabel('Number of occurrences')
        plt.xlabel('Timing tool (ps)')
#        plt.subplot(gs[0,1])
#        plt.plot(IOVec)
#        plt.ylabel('I0')
#        plt.xlabel('Event number')
        
        plt.subplot(gs[1,1])
#        plt.hist(photonEnVec,400,histtype='stepfilled')
        #offset = np.min(monoEn)
        offset = 523.5
        plt.hist(1000*(monoEn-offset),400,histtype='stepfilled')
        plt.ylabel('Number of occurrences')
        plt.xlabel('Beam energy after monochromator minus '+str(offset)+'eV (meV)')
#        plt.xticks(np.linspace(np.min(monoEn),np.max(monoEn),3))
        
        plt.subplot(gs[2,1])
        plt.hist(I0Vec,400,histtype='stepfilled')
        plt.ylabel('Number of occurrences')
        plt.xlabel('I0 (gas monitor)')
        #plt.xlabel('I0 (gas detector before monochromator - f_11_ENRC')
        plt.show()
        
        legvec = np.append(legvec,"Run"+str(i))
           
    plt.subplot(gs[:,0])
    plt.legend(legvec)
    

def plotAllCorrections(runnum,labelStr):
    [RIXSSumm_raw, ImSumm_raw, I0Vec, I0Summ, photonEnVec]=RIXS_funcs.hdf5AndFile_read(runnum,cosmicsMaskOn=1)
    
    [RIXSSumm_cosmics, ImSumm_cosmics, I0Vec, I0Summ, photonEnVec]=RIXS_funcs.hdf5AndFile_read(runnum,cosmicsMaskOn=0)
    
    energyAxis = energyCalib()
    
#    threshold = np.mean(ImSumm_cosmics[0:100,:])
    threshold = np.mean(ImSumm_cosmics)
    RIXSSumm_cosmics_threshold, ImSumm_cosmics_threshold, dummy = thresholdCheck(threshold, ImSumm_cosmics)
    
    plt.figure(501,figsize=(20, 10))
    gs = gridspec.GridSpec(3, 3, width_ratios=[4, 1, 4]) 
    
    plt.subplot(gs[0,0])
    plt.imshow(ImSumm_raw, vmin=np.min(ImSumm_raw), vmax=np.max(ImSumm_raw)/10, label=labelStr)
    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
    plt.title('No corrections')
    plt.colorbar()
    
    plt.subplot(gs[1,0])
    plt.imshow(ImSumm_cosmics, vmin=np.min(ImSumm_cosmics), vmax=np.max(ImSumm_cosmics)/10, label=labelStr)
    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
    plt.title('Cosmics removed')
    plt.colorbar()
    
    plt.subplot(gs[2,0])
    plt.imshow(ImSumm_cosmics_threshold, vmin=np.min(ImSumm_cosmics_threshold), vmax=np.max(ImSumm_cosmics_threshold)/10, label=labelStr)
    plt.xlabel('Pixels')
    plt.ylabel('Pixels')
    plt.title('Cosmics and threshold removed')
    plt.colorbar()
    
    plt.subplot(gs[0,2])
    plt.plot(energyAxis, RIXSSumm_raw, label=labelStr)
    plt.xlabel('Energy (eV)')
    plt.ylabel('RIXS intensity')
    plt.title('No corrections')
    
    plt.subplot(gs[1,2])
    plt.plot(energyAxis, RIXSSumm_cosmics, label=labelStr)
    plt.xlabel('Energy (eV)')
    plt.ylabel('RIXS intensity')
    plt.title('Cosmics removed')
    
    plt.subplot(gs[2,2])
    plt.plot(energyAxis, RIXSSumm_cosmics_threshold, label=labelStr)
    plt.xlabel('Energy (eV)')
    plt.ylabel('RIXS intensity')
    plt.title('Cosmics and threshold removed')
                    
    
def thresholdCheck(threshold, ImSumm):
    mask = ImSumm > threshold
    ImSumm = ImSumm*mask
    masknew = mask*threshold
    ImSummBase = ImSumm-masknew
    RIXSSumm = np.sum(ImSummBase,axis=1)
    #maskSummx = np.sum(mask,axis=1)
    #maskSummy = np.sum(mask,axis=0)
    maskSummy = np.sum(mask,axis=1)    
    return RIXSSumm, ImSummBase, maskSummy

def removeThreshold(threshold,ImSumm):
    ImSumm = ImSumm-threshold
    mask = ImSumm > 0
    ImSumm = ImSumm*mask
    RIXSSumm = np.sum(ImSumm,axis=1)
    return RIXSSumm, ImSumm
    
def AssignError(RIXSData,xrng=100):
    energy = energyCalib()
    #plt.plot(energy,RIXSTest)
    fitres = np.polyfit(energy[0:xrng],RIXSData[0:xrng],1)  

    line = fitres[1]+fitres[0]*energy
    #plt.plot(energy,line) 
    errorAvg = np.sqrt(np.mean((RIXSData[0:xrng]-line[0:xrng])**2))
    return errorAvg







  
    