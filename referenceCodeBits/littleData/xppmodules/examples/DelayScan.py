# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 21:31:56 2015

@author: snelson
"""
import h5py
import numpy as np
from matplotlib import pyplot as plt
plt.ion()

################
#function to check if a given variable in contained in the hdf5 file
################
def hasKey(fh5, inkey, printThis=False):
    hasKey=False
    for key in fh5.keys():
        for skey in fh5[key].keys():
            if inkey.find('%s/%s'%(key,skey))>=0:
                if printThis:
                    print 'found: %s/%s in %s'%(key,skey,inkey)
                hasKey=True
    return hasKey

################
#get the delay, including the timetool/jitter correction if requested.
################
def getDelay(inh5, use_ttCorr=True):
    #new delay scan
    if hasKey(inh5, 'enc/lasDelay'):
        nomDelay=inh5['enc/lasDelay'].value
    #standard delay scan
    else:
        for key in self.fh5['scan'].keys():
            if key.find('var')<0 and key.find('none')<0:
                isScan=True
                scanVar=key
        if isScan:
            nomDelay=inh5[scanVar].value
        if nomDelay.max()<1e-9:
            nomDelay*=1e12
    if use_ttCorr:
        ttCorr=inh5['tt/ttCorr'].value
        return ttCorr+nomDelay
    else:
        return nomDelay

################
#get array for variables from hdf5 file. Apply ROI if given & sum over remaining axis to get single value/event
################
def get1dVar(inh5, plotvar,threshold=-1e25):
    #get the signal variable
    if isinstance(plotvar,list):
        sigROI = plotvar[1]
        plotvar = plotvar[0]
    else:
        sigROI=[]
    if not hasKey(inh5, plotvar):
        print 'signal variable %s not in littleData file'%(plotvar)
        return

    vals = inh5[plotvar].value.squeeze()
    if threshold!=-1e25:
        vals = vals[vals<threshold]=0
    if len(vals.shape)>1:
        if sigROI!=[]:
            if len(vals.shape)==2:
                if not isinstance(sigROI, list):
                    vals=vals[:,sigROI]
                elif len(sigROI)>1:
                    vals=vals[:,sigROI[0]:sigROI[1]]
                else:
                    vals=vals[:,sigROI[0]]
            elif len(vals.shape)==3:
                if not isinstance(sigROI, list):
                    vals=vals[:,sigROI]
                elif len(sigROI)==1:
                    vals=vals[:,sigROI[0]]
                elif len(sigROI)==2:
                    vals=vals[:,sigROI[0]:sigROI[1],:]
                else:
                    vals=vals[:,sigROI[0]:sigROI[1],sigROI[2]:sigROI[3]]
            else:
                print 'this dimension is not yet implemented:',len(sigROI.shape)
    while len(vals.shape)>1:
        vals = vals.sum(axis=1)
    return vals

################
# get array of bools (True/False) for events passing a set of cuts/filter, e.g.
# [['lightStatus/xray',0.5,1.5],['ipm2/sum',0.2,5]]
################
def getFilter(fh5, cuts=[]):
    total_filter=np.ones_like(fh5['scan/var0'].value).astype(bool)
    filters=[]
    for thiscut in cuts:
        thisPlotvar=get1dVar(fh5,thiscut)
        filters.append(~np.isnan(thisPlotvar))
        if len(thiscut)==3:
            filters.append((thisPlotvar > thiscut[1]) & (thisPlotvar < thiscut[2]))
        else:
            filters.append(thisPlotvar != thiscut[1])
    for ft in filters:
        total_filter&=ft                
    return total_filter

################
# plot the signal variable, normalized by an i0 variable in bins of the laser/xray delay
# Bins can be number of bins (int) or step size (float) (min/max will be taken from scan variable), 3# defining start/end & (N bins or stepSize) or array of bin boundaries
# optionally takes cuts like
# [['lightStatus/xray',0.5,1.5],['ipm2/sum',0.2,5]]
################
def plotDelayScan(fh5, ttCorr=True, sig='', i0='', Bins=100, returnData=False, cuts=[]):
    plotVar=''
    if sig!='':
        sigVal = get1dVar(fh5, sig)
        for sigp in sig:
            if isinstance(sigp,basestring):
                plotVar+=sigp.replace('/','_')
            elif isinstance(sigp,list):
                for bound in sigp:
                    plotVar+='-%g'%bound
    else:
        print 'could not get signal variable:', sig
 
    if i0!='':
        i0Val = get1dVar(fh5, i0)
        plotVar+='/'
        for i0p in i0:
            if isinstance(i0p,basestring):
                plotVar+=i0p.replace('/','_')
            elif isinstance(i0p,list):
                for bound in i0p:
                    plotVar+='-%g'%bound
    else:
        print 'could not get monitoring variable:', i0
         
    #get the scan variable & time correct if desired
    delays=getDelay(fh5, use_ttCorr=ttCorr)
    if ttCorr:
        scanVarName='delay (tt corrected) [fs]'
    else:
        scanVarName='delay [fs]'
 
    FilterOn = getFilter(fh5, cuts)           
    print 'selected ',delays[FilterOn].shape[0],' of ',delays.shape[0]

    scanPoints = np.arange(Bins[0] , Bins[1], Bins[2])
    if isinstance(Bins[2], int):
        scanPoints = np.linspace(Bins[0] , Bins[1], Bins[2])
    scanOnIdx = np.digitize(delays[FilterOn], scanPoints)
    scanPoints = np.concatenate([scanPoints, [scanPoints[-1]+(scanPoints[1]-scanPoints[0])]],0)

    # calculate the normalized intensity for each bin
    iNorm = np.bincount(scanOnIdx, i0Val[FilterOn])
    iSig = np.bincount(scanOnIdx, sigVal[FilterOn])
    scan = iSig/iNorm
    #scan = scan/np.mean(scan[1]) # normalize to 1 for first energy point?

    returnDict= {'scanVarName':scanVarName,'scanPoints':scanPoints,'scan':scan,'plotVarName':plotVar}

    plotVarName = returnDict['plotVarName']
    scanVarName = returnDict['scanVarName']
    scanPoints = returnDict['scanPoints']
    scan = returnDict['scan']
        
    fig=plt.figure(figsize=(10,5))
    plt.plot(scanPoints, scan, 'ro--', markersize=5)
    plt.xlabel(scanVarName)
    plt.ylabel(plotVarName)
    plt.ylim(np.nanmin(scan)*0.95,np.nanmax(scan)*1.05)
    plt.xlabel(scanVarName)
    plt.ylabel(plotVarName)
      
    return returnDict       


################
# 
# Main
# 
################
#set our filters    
cuts=[]
cuts.append(['lightStatus/xray',0.5,1.5])
cuts.append(['lightStatus/laser',0.5,1.5])
cuts.append(['ipm2/sum',0.05,5.])
cuts.append(['tt/FLTPOSFWHM',90,120])

#open the hdf5 file & plot the data
#we are using only 3 channels of ipm3 as one diode is unresponsive for our i0
#signal is a PIPS diode read out in our user IPM box (diodeU), here attached to channel 1
fh5 = h5py.File('/reg/d/psdm/xpp/xpptut15/ftc/ldat_xpptut15_Run251.h5','r')
plotDelayScan(fh5,sig=['diodeU/channels',[1,2]],i0=['ipm3/channels',[1,4]],cuts=cuts,Bins=[0.5,1.8,0.02])

fh252 = h5py.File('/reg/d/psdm/xpp/xpptut15/ftc/ldat_xpptut15_Run252.h5','r')
plotDelayScan(fh252,sig=['diodeU/channels',[1,2]],i0=['ipm3/channels',[1,4]],cuts=cuts,Bins=[0.,15,0.02])
