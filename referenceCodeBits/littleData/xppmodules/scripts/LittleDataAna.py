"""
Created on Tue Dec  8 21:31:56 2015

@author: snelson
"""
import h5py
from os import path
import numpy as np
from pylab import ginput
from matplotlib import pyplot as plt
from matplotlib import gridspec
from scipy import interpolate
from utilities import getTTstr
from utilities import hasKey as util_hasKey
from utilities import getDelay as util_getDelay
from utilities import dictToHdf5
import json
import subprocess
import socket
from utilities import hist2d
from scipy import sparse
plt.ion()

class photons(object):
    def __init__(self,h5file,detName='epix',photName='photon'):
        self._detName=detName
        self._photName=photName
        if self._photName[-1]!='_':
            self._photName+='_'
        self._h5 = h5file
        self.shape = h5file['UserDataCfg/'+detName+'_cmask'].value.shape

    def getKeys(self):
        keyList=[]
        for data in self.__dict__.keys():
            if not data[0]=='_':
                keyList.append(data)
        return keyList

    def fillPhotArrays(self):
        eh5_dir = self._h5[self._detName]
        for key in eh5_dir.keys():
            if not (key.find(self._photName)>=0):
                continue
            #likely a different photName set of variables. Need own fillPhotArray
            if key.replace(self._photName,'').find('_')>=0:
                continue
            h5Name = self._photName+key.replace(self._photName,'')
            #print 'h5name ',h5Name
            keyName=key.replace(self._photName,'')
            self.__dict__[keyName] = eh5_dir[h5Name].value
        
    def flattenPhotArray(self, filterArray=None):
        for key in self.getKeys():
            if filterArray is None:
                filterArray=np.ones(self.__dict__[key].shape[0])
            if filterArray.shape == self.__dict__[key].shape[0]:
                self[key] = self.__dict__[key][filterArray].flatten()

    def photImgEvt(self, iEvt):
        eh5_dir = self._h5[self._detName]
        data = eh5_dir[self._photName+'data'][iEvt]
        row = eh5_dir[self._photName+'row'][iEvt]
        col = eh5_dir[self._photName+'col'][iEvt]
        if max(row)>=self.shape[0] or max(col)>=self.shape[1]:
            print 'inconsistent shape ',self.shape, max(row), max(col)
        #print eh5_dir[self._photName+'data'][iEvt].shape
        #print eh5_dir[self._photName+'row'].shape
        #print eh5_dir[self._photName+'row'][iEvt].shape
        #print max(eh5_dir[self._photName+'row'][iEvt])
        #print 'inconsistent shape ',self.shape, max(row), max(col)
        return sparse.coo_matrix( (data, (row, col)),shape=self.shape ).todense()

    def photImg(self, filterArray=None):
        if 'pHist' not in self.__dict__.keys():
            self.fillPhotArrays()
        if filterArray is None:
            filterArray=np.ones(self.pHist.shape[0]).astype(bool)
        data = self.data[filterArray].flatten()
        data = data[data>0]
        row = self.row[filterArray].flatten()[data>0]
        col = self.col[filterArray].flatten()[data>0]
        img = sparse.coo_matrix( (data, (row, col)) ).todense()
        return img

    def photonHist(self, filterArray=None):
        if 'pHist' not in self.__dict__.keys():
            self.fillPhotArrays()
        if filterArray is None:
            filterArray=np.ones(self.pHist.shape[0]).astype(bool)
        if filterArray.shape[0] == self.pHist.shape[0]:
            pHist = self.pHist[filterArray].sum(axis=0)
        else:
            return
        return pHist

class droplets(object):
    def __init__(self,h5file,detName='epix',dropName='droplet'):
        self._detName=detName
        self._dropName=dropName
        if self._dropName[-1]!='_':
            self._dropName+='_'
        self._h5 = h5file

    def getKeys(self):
        keyList=[]
        for data in self.__dict__.keys():
            if not data[0]=='_':
                keyList.append(data)
        return keyList

    def fillDropArrays(self):
        eh5_dir = self._h5[self._detName]
        for key in eh5_dir.keys():
            if not (key.find(self._dropName)>=0):
                continue
            #likely a different dropName set of variables. Need own fillDropArray
            if key.replace(self._dropName,'').find('_')>=0:
                continue
            h5Name = self._dropName+key.replace(self._dropName,'')
            keyName=key.replace(self._dropName,'')
            self.__dict__[keyName] = eh5_dir[h5Name].value
        
    def flattenDropArray(self, filterArray=None):
        if filterArray is None:
            if 'npix' in self.getKeys():
                filterArray = (self.__dict__['npix']>0)
            else:
                print 'did not find npix, will not flatten'
                return

        for key in self.getKeys():
            if filterArray.shape == self.__dict__[key].shape:
                self.__dict__[key] = self.__dict__[key][filterArray].flatten()

    def getDropPixels(self, ievt, debug=False):
        if not 'Pix' in self.__dict__.keys():
            nDroplets = self._h5[self._detName][self._dropName+'nDroplets'][ievt]
            Pix = self._h5[self._detName][self._dropName+'Pix'][ievt]
            sizeX = self._h5[self._detName][self._dropName+'bbox_x1'][ievt] - self._h5[self._detName][self._dropName+'bbox_x0'][ievt]
            sizeY = self._h5[self._detName][self._dropName+'bbox_y1'][ievt] - self._h5[self._detName][self._dropName+'bbox_y0'][ievt]
            adu = self._h5[self._detName][self._dropName+'adu'][ievt]
            dX =  self._h5[self._detName][self._dropName+'X'][ievt]
            dY =  self._h5[self._detName][self._dropName+'Y'][ievt]
        else:
            nDroplets = self.nDroplets[ievt]
            Pix = self.Pix[ievt]
            sizeX = self.bbox_x1[ievt] - self.bbox_x0[ievt]
            sizeY = self.bbox_y1[ievt] - self.bbox_y0[ievt]
            adu = self.adu[ievt]
            dX =  self.X[ievt]
            dY =  self.Y[ievt]
        sizes = (sizeX*sizeY)
        imgs=[]
        idxPix=0
        for iDrop in range(0,nDroplets):
            img= np.array(Pix[idxPix:(idxPix+sizes[iDrop])]).reshape(sizeX[iDrop],sizeY[iDrop])
            if debug:
                print 'adu ',adu[iDrop],img.sum()
            imgs.append(img)
            idxPix+=sizes[iDrop]
        ret_dict = {'images' : imgs}
        ret_dict['adu']=adu[:len(imgs)]
        ret_dict['X']=dX[:len(imgs)]
        ret_dict['Y']=dY[:len(imgs)]
        return ret_dict

    def getDropPixelsRoi(self, ievt, mask, debug=False):
        dropInfo = self.getDropPixelsRoi(ievt, debug=debug)
        imgsROI = []
        for img,x,y in zip(dropInfo['images'],dropInfo['X'],dropInfo['Y']):
            if mask(int(x), int(y))==1:
                imgsROI.append(img)
        return imgsROI

    def plotSpectrum(self, plotLog=True, aduRange=[]):
        if len(aduRange)==0:
            aduRange=[0,700]
        elif len(aduRange)==1:
            aduRange=[0,aduRange[0]]
        elif len(aduRange)==2:
            aduRange=[aduRange[0], aduRange[1]]
            
        hst = np.histogram(self.__dict__['adu'], np.arange(aduRange[0],aduRange[1]))
        if plotLog:
            plt.plot(hst[1][1:],np.log(hst[0]),'o')
        else:
            plt.plot(hst[1][1:],hst[0],'o')
            
    def plotAduX(self, ADUrange=[120,180],maxLim=99.5):
        if len(self.__dict__['X'].shape)>1:
            self.flattenDropArray()
        plt.clf()
        hist2d(self.__dict__['X'],self.__dict__['adu'], numBins=[702,180], histLims=[0,702,ADUrange[0], ADUrange[1]],limits=[1,maxLim])

    def plotAduY(self, ADUrange=[120,180],maxLim=99.5):    
        if len(self.__dict__['Y'].shape)>1:
            self.flattenDropArray()
        plt.figure()
        plt.subplot(211)
        hist2d(self.__dict__['Y'][self.__dict__['X']<351],self.__dict__['adu'][self.__dict__['X']<351], numBins=[766,180], histLims=[0,766,ADUrange[0], ADUrange[1]],limits=[1,maxLim])
        plt.subplot(212)
        hist2d(self.__dict__['Y'][self.__dict__['X']>353],self.__dict__['adu'][self.__dict__['X']>353], numBins=[766,180], histLims=[0,766,ADUrange[0], ADUrange[1]],limits=[1,maxLim])

    def plotXY(self, ADUrange=[120,180]):            
        dx = self.__dict__['X'][self.__dict__['adu']>ADUrange[0]]
        dy = self.__dict__['Y'][self.__dict__['adu']>ADUrange[0]]
        dadu = self.__dict__['adu'][self.__dict__['adu']>ADUrange[0]]
            
        plt.clf()
        ndrop_int = max(1,490000./dx[dadu<ADUrange[1]].shape[0])
        hist2d(dx[dadu<ADUrange[1]],dy[dadu<ADUrange[1]], numBins=[int(702/ndrop_int),int(766/ndrop_int)])


class Cube(object):
    def __init__(self, binVar, bins=[], cubeName=None, SelName='def'):
        self.binVar = binVar
        self.bins = bins
        self.SelName = SelName

        nbins = len(bins)
        if nbins==3:
            if type(bins[2]) is int:
                nbins=len(np.linspace(min(bins[0],bins[1]),max(bins[0],bins[1]),bins[2]))
            else:
                nbins=len(np.arange(min(bins[0],bins[1]),max(bins[0],bins[1]),bins[2]))

        if cubeName is not None:
            self.cubeName = cubeName
        else:
            if binVar.find('/')>=0:
                self.cubeName = '%s_%i'%(binVar.replace('/','__'), nbins)
            else:
                self.cubeName = '%s_%i'%(binVar, nbins)
        self.targetVars=[]
    def addVar(self, tVar):
        self.targetVars.append(tVar)
    def printCube(self, Sel):
        print 'cube: ',self.cubeName
        if len(self.bins)==3 and type(self.bins[2]) is int:
            print '%s binned from %g to %g in %i bins'%(self.binVar,self.bins[0],self.bins[1],self.bins[2])
        elif len(self.bins)==3:
            print '%s binned from %g to %g in %i bins'%(self.binVar,self.bins[0],self.bins[1],int((self.bins[1]-self.bins[0])/self.bins[2]))
        elif  len(self.bins)==0:
            print 'will use scan steps for binning'
        else:
            print '%s binned from %g to %g in %i bins'%(self.binVar,min(self.bins),max(self.bins),len(self.bins))
        for icut,cut in enumerate(Sel.cuts):
            print 'Cut %i: %f < %s < %f'%(icut, cut[1], cut[0],cut[2])
        print 'we will bin: ',self.targetVars

class Selection(object):
    def __init__(self, Name='def'):
        self.name = Name
        self.cuts=[]
    def addCut(self, varName, varmin, varmax):
        self.cuts.append([varName, varmin, varmax])
    def removeCut(self, varName):
        for cut in self.cuts:
            if cut[0]==varName: self.cuts.remove(cut)
    def printCuts(self):
        for icut,cut in enumerate(self.cuts):
            print 'Cut %i: %f < %s < %f'%(icut, cut[1], cut[0],cut[2])
    def add(self, additionalSel):
        for cut in additionalSel.cuts:
            self.cuts.append(cut)

class LittleDataAna(object):
    def __init__(self, expname='', run=-1, dirname='', filename=''):
        self.expname=expname
        self.run=run
        self.hutch=self.expname[:3]
        if dirname=='':
            self.dirname='/reg/d/psdm/%s/%s/ftc'%(self.hutch,self.expname)
            #run 14 and beyond.
            if not path.isdir(self.dirname):
                self.dirname='/reg/d/psdm/%s/%s/hdf5/smalldata'%(self.hutch,self.expname)
        else:
            self.dirname=dirname
        if filename == '':
            self.fname='%s/ldat_%s_Run%03d.h5'%(self.dirname,self.expname,self.run)
        else:
            self.fname='%s/%s'%(self.dirname,filename)
        print 'and now open in dir: ',self.dirname,' to open file ',self.fname
        self.cubes=[]
        self.jobIds=[]
        self.Sels = {'def': Selection()}
        if path.isfile(self.fname):
            self.fh5=h5py.File(self.fname)
            self.ttCorr, self.ttBaseStr = getTTstr(self.fh5)
            self.thumb_scan=self.get1dVar('scan/var0')
            try:
                self.thumb_i0=self.get1dVar('ipm3/sum')
            except:
                self.thumb_i0=None
            self.thumb_sig=None
            self.thumb_delay=None
            #self.thumb_delay=self.getDelay()
            #for key in self.Keys():
            #    if key.find('ROI')>=0 or key.find('roi')>=0:
            #        self.thumb_sig=self.get1dVar(key)
            #if self.thumb_sig is None:
            #    self.thumb_sig=self.get1dVar('diodeU/sum')
            #if len(self.Keys2d())>0:
            #    self.thumb_sig2d=self.fh5[self.Keys2d()[0]]
            #else:
            #    self.thumb_sig2d=None
        else: #if path.isfile(self.fname):
            print 'could not find file: ',self.fname
            return None
    def setThumb(self, key, data):
        if isinstance(data,basestring):
            if key.find('2d')<0:
                dataArray = self.get1dVar(data)
        elif isinstance(data,list) and isinstance(data[0],basestring):
            if key.find('2d')<0:
                dataArray = self.get1dVar(data)
        else:
            dataArray = data
        if key=='i0':
            self.thumb_i0 = dataArray
        elif key=='scan':
            self.thumb_scan = dataArray
        elif key=='sig':
            self.thumb_sig = dataArray
        elif key=='sig2d':
            self.thumb_sig2d = dataArray
    def setRun(self, run):
        self.run=run
        self.fname='%s/ldat_%s_Run%03d.h5'%(self.dirname,self.expname,self.run)
        if path.isfile(self.fname):
            self.fh5=h5py.File(self.fname)
            if self.hasKey('tt/ttCorr'):
                self.ttCorr = 'tt/ttCorr'
            elif self.hasKey('ttCorr/tt'):
                self.ttCorr = 'ttCorr/tt'
            else:
                self.ttCorr = None
            self.ttBaseStr = 'tt/'
            if not self.hasKey(self.ttBaseStr+'AMPL'):
                if self.hasKey('tt/XPP_TIMETOOL_AMPL'):
                    self.ttBaseStr = 'tt/XPP_TIMETOOL_'
                elif self.hasKey('tt/TIMETOOL_AMPL'):
                    self.ttBaseStr = 'tt/TIMETOOL_'
                elif self.hasKey('tt/TTSPEC_AMPL'):
                    self.ttBaseStr = 'tt/TTSPEC_'
            self.thumb_scan=self.get1dVar('scan/var0')
            try:
                self.thumb_i0=self.get1dVar('ipm3/sum')
            except:
                self.thumb_i0=None
            self.thumb_sig=None
            self.thumb_delay=None
            self.thumb_sig2d=None
    def setExperiment(self,expname):
        self.expname=expname
        self.fname='%s/ldat_%s_Run%03d.h5'%(self.dirname,self.expname,self.run)
        if path.isfile(self.fname):
            self.fh5=h5py.File(self.fname)
    def setLittleDataDir(self, dirname):
        self.dirname=dirname
        self.fname='%s/ldat_%s_Run%03d.h5'%(self.dirname,self.expname,self.run)
        if path.isfile(self.fname):
            self.fh5=h5py.File(self.fname)
    def Keys2d(self, inh5 = None, printKeys=False):
        return self.Keys(inh5 = inh5, printKeys=printKeys, areaDet=True)
    def Keys(self, name=None, inh5 = None, printKeys=False, areaDet=False, cfgOnly=False):
        keys = []
        if inh5 == None and self.fh5:
            fh5 = self.fh5
        else:
            fh5 = hf5        
        if fh5:
            for key in fh5.keys():
                if cfgOnly and not key.find('Cfg')>=0:
                    continue
                if areaDet and key.find('Cfg')>=0:
                    continue
                if isinstance(name, basestring) and key.find(name)<0:
                    continue
                for skey in fh5[key].keys():
                    thiskey = '%s/%s'%(key,skey)
                    if len(fh5[thiskey].shape)<=2 and areaDet:
                        continue
                    if isinstance(name, basestring) and thiskey.find(name)<0:
                        continue
                    keys.append(thiskey)
                    if printKeys:
                        print thiskey
        return keys
    def printSelection(self, selName=None, brief=True):
        if selName is not None:
            if selName not in self.Sels:
                print 'could not find selection ',selName,', options are: ',
                for sel in self.Sels:
                    print sel
                return
            print self.Sels[selName].printCuts()
            return
        for sel in self.Sels:
            print sel
            if not brief:
                print self.Sels[sel].printCuts()
                print '--------------------------'
    def nEvts(self,printThis=False):
        if self.fh5:
            nent = self.fh5['scan/var0'].value.shape[0]
            if printThis:
                print 'Number of events in %s is %i'%(self.fname, nent)
            return nent
    def printRunInfo(self):
        self.nEvts(printThis=True)
        isScan=False
        scanVar=''
        for key in self.fh5['scan'].keys():
            if key.find('var')<0 and key.find('none')<0:
                isScan=True
                scanVar=key
        if isScan:
            nPoints=np.unique(self.fh5['scan/%s'%scanVar].value).shape[0]
            print 'this run is a scan of %s with %d points'%(scanVar,nPoints)
    def hasKey(self, inkey, inh5=None, printThis=False):
        if inh5 == None and self.fh5:
            fh5 = self.fh5
        else:
            fh5 = hf5
        return util_hasKey(inkey, fh5, printThis)

    def addCut(self, varName, cmin, cmax, SelName='def'):
        if not self.Sels.has_key(SelName):
            self.Sels[SelName] = Selection()
        self.Sels[SelName].addCut(varName, cmin,cmax)
    def removeCut(self, varName, SelName='def'):
        if not self.Sels.has_key(SelName):
            print 'Selection with name %s does not exist, cannot remove cut'%SelName
            return
        self.Sels[SelName].removeCut(varName)
    def printCuts(self, SelName='def'):
        self.Sels[SelName].printCuts()

    def getFilterLaser(self, SelName='def', ignoreVar=[]):
        ignoreVar.append('lightStatus/laser')
        onFilter = self.getFilter(SelName=SelName, ignoreVar=ignoreVar)
        if self.ttCorr is not None:
            ignoreVar.append(self.ttCorr)
        if self.hasKey(self.ttBaseStr+'AMPL'):
            ignoreVar.append(self.ttBaseStr+'AMPL')
            ignoreVar.append(self.ttBaseStr+'FLTPOS')
            ignoreVar.append(self.ttBaseStr+'FLTPOS_PS')
            ignoreVar.append(self.ttBaseStr+'FLTPOSFWHM')
        offFilter = self.getFilter(SelName=SelName, ignoreVar=ignoreVar)
        #return [onFilter, offFilter]

        FilterOff = (offFilter&[self.fh5['lightStatus/laser'].value!=1])
        FilterOn = (onFilter&[self.fh5['lightStatus/laser'].value==1])
        return [FilterOn.squeeze() , FilterOff.squeeze()]

    def getFilter(self, SelName=None, ignoreVar=[]):
        total_filter=np.ones_like(self.fh5['scan/var0'].value).astype(bool)
        if SelName==None:
            return total_filter
        filters=[]
        for thiscut in self.Sels[SelName].cuts:
            if not thiscut[0] in ignoreVar:
                thisPlotvar=self.get1dVar(thiscut[0])
                filters.append(~np.isnan(thisPlotvar))
                if len(thiscut)==3:
                    filters.append((thisPlotvar > thiscut[1]) & (thisPlotvar < thiscut[2]))
                else:
                    filters.append(thisPlotvar != thiscut[1])
        for ft in filters:
            total_filter&=ft                
        return total_filter

    def saveFilter(self, baseName='boolArray',SelName=None, ignoreVar=[]):
        total_filter = self.getFilter(SelName=SelName, ignoreVar=ignoreVar)
        np.savetxt('%s_Run%03d.txt'%(baseName, self.run),total_filter.astype(bool),fmt='%5i')

    def getSelIdx(self, SelName='def'):
        fids = self.fh5['EvtID/fid'].value
        times = self.fh5['EvtID/time'].value
        Filter =  self.getFilter()
        selfids = [ (ifid,itime) for ifid,itime in zip(fids[Filter],times[Filter])]
        return selfids
        
    def getRedVar(self, plotvar,threshold=-1e25):
        #get the signal variable
        if isinstance(plotvar,list):
            sigROI = plotvar[1]
            plotvar = plotvar[0]
        else:
            sigROI=[]
        if not self.hasKey(plotvar):
            print 'signal variable %s not in littleData file'%(plotvar)
            return

        vals = self.fh5[plotvar].value.squeeze()

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
                    print 'this dimension is not yet implemented:',len(sig.shape)
        return vals

    def get1dVar(self, plotvar,threshold=-1e25):
        vals = self.getRedVar(plotvar,threshold)
        while len(vals.shape)>1:
            vals = vals.sum(axis=1)
        return vals

    def getDelay(self, use_ttCorr=True, addEnc=False):
        if self.thumb_delay!=None:
            return self.thumb_delay

        self.thumb_delay = util_getDelay(self.fh5, use_ttCorr, addEnc)
        return self.thumb_delay 

    def getPeak(self, plotvar, numBins=[100],setCuts=None, applyCuts=None, limits=[1,99],fig=None,asHist=False,sigROI=[]):
        hst = plotVar(plotvar, numBins=[100],setCuts=None, applyCuts=None, limits=[1,99],fig=None,asHist=False,sigROI=[])
        if len(hst)==2:
            return [hst[0].max(), hst[1][hst[0].argmax()]]
        else:
            print 'getPeak is not yet implemented for this type of data (need 1d histo)'

    def plotVar(self, plotvar, numBins=[100],setCuts=None, applyCuts=None, limits=[1,99],fig=None,asHist=False):
        if not isinstance(numBins, (list, tuple)):
            numBins = [numBins]
        if isinstance(plotvar, basestring) or (len(plotvar)==2 and (isinstance(plotvar[0], basestring) and not isinstance(plotvar[1], basestring))):
            if len(numBins)!=1:
                print 'bin# needs to be of same dimensions as plotvariables (1d)'
                return
            return self.plotVar1d(plotvar, numBins=numBins[0],setCuts=setCuts, applyCuts=applyCuts, limits=limits,fig=fig)
        elif len(plotvar)>2:
            print 'plotting of 3 variables is not defined yet'
            return
        if len(numBins)!=2:
            if len(numBins)==1:
                numBins=[numBins[0],numBins[0]]
            else:
                print 'bin# needs to be of same dimentions as plotvariables (2d)'
        return self.plotVar2d(plotvar, numBins=numBins,setCuts=setCuts, applyCuts=applyCuts, limits=limits,fig=fig,asHist=asHist)

    def plotVar1d(self, plotvar, numBins=100,setCuts=None, applyCuts=None, limits=[1,99],fig=None):
        if isinstance(plotvar,list):
            if not (self.hasKey(plotvar[0]) or plotvar[0]=='delay'): 
                print 'request variable %s not in littleData file'%plotvar
                return
        else:
            if not (self.hasKey(plotvar) or plotvar=='delay'): 
                print 'request variable %s not in littleData file'%plotvar
                return
        if plotvar=='delay':
            vals = self.getDelay(use_ttCorr=True)
        elif len(plotvar)==1 and plotvar.find('droplets')>=0:
            vals = self.fh5[plotvar].value
        else:
            vals = self.get1dVar(plotvar)

        total_filter = np.ones(vals.shape[0]).astype(bool)
        if applyCuts is not None and self.Sels.has_key(applyCuts):
            total_filter =  self.getFilter(applyCuts, [plotvar])
        vals = vals[total_filter]

        if  len(plotvar)==1 and plotvar.find('droplets')>=0:
            vals = vals.flatten()[vals.flatten()>0]

        if abs(limits[0]-50)<=50 and abs(limits[1]-50)<=50:
            pmin = np.percentile(vals,limits[0])
            pmax = np.percentile(vals,limits[1])
            if np.isnan(pmin): pmin=np.nanmin(vals)
            if np.isnan(pmax): pmax=np.nanmax(vals)
        else:
            pmin=min(limits[0],limits[1])
            pmax=max(limits[0],limits[1])
        hst = np.histogram(vals,np.linspace(pmin,pmax,numBins))
        print 'plot %s from %g to %g'%(plotvar,pmin,pmax)
        if fig is None:
            fig=plt.figure(figsize=(8,5))

        plt.plot(hst[1][:-1],hst[0],'o')
        plt.xlabel(plotvar)
        plt.ylabel('entries')
        if setCuts is not None and self.Sels.has_key(setCuts):
            p = np.array(ginput(2))
            p=[p[0][0],p[1][0]]
            self.Sels[setCuts].addCut(plotvar,min(p),max(p))
        return hst

    def plotVar2d(self, plotvars, setCuts=None, applyCuts=None, limits=[1,99], asHist=False,numBins=[100,100],fig=None):
        for plotvar in plotvars:
            if isinstance(plotvar,list):
                plotvar = plotvar[0]
            if not self.hasKey(plotvar) or plotvar == 'delay': 
                print 'request variable %s not in littleData file'%(plotvar)
        vals=[]
        for plotvar in plotvars:
            if plotvar == 'delay':
                vals=self.getDelay(use_ttCorr=True)
            #elif len(plotvar)==1 and plotvar.find('droplets')>=0:
            #    vals = self.fh5[plotvar].value
            else:   
                vals.append(self.get1dVar(plotvar))
            if len(vals[-1].shape)!=1:
                print 'variable %s does not return a scalar, this is not yet implemented'%plotvar
        pmin0 = np.nanmin(vals[0]); pmin1 = np.nanmin(vals[1]);
        pmax0 = np.nanmax(vals[0]); pmax1 = np.nanmax(vals[1]);
        if limits[0]>0:
            if not np.isnan(np.percentile(vals[0],limits[0])):
                pmin0 = np.percentile(vals[0],limits[0])
            if not np.isnan(np.percentile(vals[1],limits[0])):
                pmin1 = np.percentile(vals[1],limits[0])
        if limits[1]<100:
            if not np.isnan(np.percentile(vals[0],limits[1])):
                pmax0 = np.percentile(vals[0],limits[1])
            if not np.isnan(np.percentile(vals[1],limits[1])):
                pmax1 = np.percentile(vals[1],limits[1])
        print 'plots %s from %g to %g and  %s from %g to %g '%(plotvars[0],pmin0,pmax0,plotvars[1],pmin1,pmax1)
        total_filter=np.ones(vals[0].shape[0]).astype(bool)
        filters=[]
        filters.append((vals[0] >= pmin0 ) & (vals[0] <= pmax0))
        filters.append((vals[1] >= pmin1 ) & (vals[1] <= pmax1))
        if applyCuts is not None and self.Sels.has_key(applyCuts):
            filters.append(self.getFilter(applyCuts,plotvars))
        for ft in filters:
            total_filter&=ft                

        print 'select ',total_filter.sum(),' of ',np.ones_like(total_filter).sum(),' events'
        
        if fig is None:
            fig=plt.figure(figsize=(8,5))

        if not asHist:
            plt.plot(vals[1][total_filter],vals[0][total_filter],'o',markersize=3)
            plt.xlabel(plotvars[1])
            plt.ylabel(plotvars[0])
        else:
            v0 = vals[0][total_filter]
            v1 = vals[1][total_filter]
            binEdges0 = np.linspace(np.nanmin(v0),np.nanmax(v0),numBins[0])
            binEdges1 = np.linspace(np.nanmin(v1),np.nanmax(v1),numBins[1])
            ind0 = np.digitize(v0, binEdges0)
            ind1 = np.digitize(v1, binEdges1)
            ind2d = np.ravel_multi_index((ind0, ind1),(binEdges0.shape[0]+1, binEdges1.shape[0]+1)) 
            iSig = np.bincount(ind2d, minlength=(binEdges0.shape[0]+1)*(binEdges1.shape[0]+1)).reshape(binEdges0.shape[0]+1, binEdges1.shape[0]+1) 
            plt.imshow(iSig,aspect='auto', interpolation='none',origin='lower',extent=[binEdges1[1],binEdges1[-1],binEdges0[1],binEdges0[-1]],clim=[np.percentile(iSig,limits[0]),np.percentile(iSig,limits[1])])
            plt.xlabel(plotvars[1])
            plt.ylabel(plotvars[0])
        if setCuts is not None and self.Sels.has_key(setCuts):
            p =np.array(ginput(2))
            p0=[p[0][1],p[1][1]]
            p1=[p[0][0],p[1][0]]
            self.Sels[setCuts].addCut(plotvars[0],min(p0),max(p0))
            self.Sels[setCuts].addCut(plotvars[1],min(p1),max(p1))
        if asHist:
            return iSig
        else:
            return vals

    def getScanValues(self,ttCorr=False,addEnc=False):
        #get the scan variable & time correct if desired
        delays=self.getDelay(use_ttCorr=ttCorr,addEnc=addEnc)
        scanOrg = self.fh5['scan/var0'].value
        scanVarName = ''
        for key in self.fh5['scan'].keys():
            if key.find('var')<0 and key.find('none')<0:
                scanVarName = key
        if scanVarName.find('lxt')>=0 or scanVarName=='':
            scan = delays
            if scanVarName == '':
                if ttCorr:
                    scanVarName='delay (tt corrected) [fs]'
                else:
                    scanVarName='delay [fs]'
        else:
            scan = scanOrg
        return scanVarName,scan

    def getScans(self, runs=[], ttCorr=False, sig='', i0='', numBins=100, applyCuts=None, offData=True):
        plotData=[]
        currRun=self.run
        for run in runs:
            self.setRun(run)
            plotData.append(self.getScan(ttCorr=ttCorr,sig=sig,i0=i0,numBins=numBins,applyCuts=applyCuts))
        self.setRun(currRun)
        if not plotData[0].has_key('scanOffPoints'):
            offData=False
        for ids,dataSet in enumerate(plotData):
            if ids==0:
                scanPoints = dataSet['scanPoints']
                scan = dataSet['scan']
            elif len(dataSet['scanPoints']) != len(scanPoints) or (dataSet['scanPoints']-scanPoints).sum()>0.:
                print 'scanPoints not the same for all runs'
                return
            else:
                scan += dataSet['scan']
        if offData:
            for ids,dataSet in enumerate(plotData):
                if ids==0:
                    scanOffPoints = dataSet['scanOffPoints']
                    scanOff = dataSet['scanOff']
                elif len(dataSet['scanOffPoints']) != len(scanPoints) or (dataSet['scanOffPoints']-scanPoints).sum()>0.:
                    print 'scanOffPoints not the same for all runs'
                    print scanOffPoints
                    print dataSet['scanOffPoints']
                    offData=False
                    break
                else:
                    scanOff += dataSet['scanOff']

            if offData:
                return {'scanVarName':dataSet['scanVarName'],'scanPoints':scanPoints,'scan':scan, 'scanOffPoints':scanOffPoints,'scanoff':scanoff}
        
        return {'scanVarName':dataSet['scanVarName'],'scanPoints':scanPoints,'scan':scan}

    def getScan(self, ttCorr=False, sig='', i0='', Bins=100, applyCuts=None):
        return self.plotScan(ttCorr=ttCorr, sig=sig, i0=i0, Bins=Bins, returnData=True, applyCuts=applyCuts, plotThis=False)

    def plotScan(self, ttCorr=False, sig='', i0='', Bins=100, plotDiff=True, plotOff=True, saveFig=False,saveData=False, returnData=False, applyCuts=None, fig=None, interpolation='', plotThis=True, addEnc=False, returnIdx=False, binVar=None):
        
        plotVar=''
        if sig!='':
            sigVal = self.get1dVar(sig)
            if sigVal is not None:
                self.setThumb('sig',sigVal)
            for sigp in sig:
                if isinstance(sigp,basestring):
                    plotVar+=sigp.replace('/','_')
                elif isinstance(sigp,list):
                    for bound in sigp:
                        plotVar+='-%g'%bound
        else:
            sigVal = self.thumb_sig
            if sigVal is None:
                print 'could not get signal variable:', sig
            else:
                plotVar+='sig'

        if i0!='':
            i0Val = self.get1dVar(i0)
            if i0Val is not None:
                self.setThumb('i0',i0Val)
            plotVar+='/'
            for i0p in i0:
                if isinstance(i0p,basestring):
                    plotVar+=i0p.replace('/','_')
                elif isinstance(i0p,list):
                    for bound in i0p:
                        plotVar+='-%g'%bound
        else:
            i0Val = self.thumb_i0
            if i0Val is None:
                print 'could not get monitoring variable:', i0
            else:
                plotVar+='i0'
        
        [FilterOn, FilterOff] = self.getFilterLaser(applyCuts)
        FilterOn = FilterOn & ~np.isnan(i0Val) & ~np.isnan(sigVal)
        FilterOff = FilterOff & ~np.isnan(i0Val) & ~np.isnan(sigVal)

        if binVar is not None:
            if binVar[0] != 'delay':
                binVal = self.get1dVar(binVar[0])
            else:
                binVal=self.getDelay(use_ttCorr=ttCorr,addEnc=addEnc)
                ttCorr = None; addEnc=None
            FilterOn = FilterOn & ~np.isnan(binVal)
            FilterOff = FilterOff & ~np.isnan(binVal)

        print 'from %i events keep %i (%i off events)'%(np.ones_like(i0Val).sum(),np.ones_like(i0Val[FilterOn]).sum(), np.ones_like(i0Val[FilterOff]).sum() )

        #get the scan variable & time correct if desired
        scanVarName,scan =  self.getScanValues(ttCorr, addEnc)
            
        # create energy bins for plot: here no need to bin!
        if (not ttCorr) and (not addEnc):
            scanPoints, scanOnIdx = np.unique(scan[FilterOn], return_inverse=True)
        else:
            if isinstance(Bins, int) or isinstance(Bins, float):
                scanUnique = np.unique(scan[FilterOn])                
                if isinstance(Bins,int):
                    scanPoints = np.linspace(scanUnique[0],scanUnique[-1],Bins)
                elif isinstance(Bins,float):
                    if (abs(scanUnique[0]-scanUnique[-1])/Bins) > 1e5:
                        print 'this are more than 100k bins! will not try....'
                        return
                    scanPoints = np.arange(scanUnique[0],scanUnique[-1],Bins)
            elif isinstance(Bins,list) or isinstance(Bins,np.ndarray):
                scanPoints = Bins
            else:
                print 'Bins: ',isinstance(Bins,list),' -- ',Bins
            scanOnIdx = np.digitize(scan[FilterOn], scanPoints)
            scanPoints = np.concatenate([scanPoints, [scanPoints[-1]+(scanPoints[1]-scanPoints[0])]],0)
        OffData=False
        if scan[FilterOff].sum()!=0:
            scanOffPoints, scanOffIdx = np.unique(scan[FilterOff], return_inverse=True)
            if len(scanOffPoints) > len(scanPoints):
                scanOffPoints = scanPoints.copy()
                scanOffIdx = np.digitize(scan[FilterOff], scanOffPoints)
            OffData = True

        if returnIdx:
            return scanOnIdx

        if binVar is not None:
            if len(binVar)==1:
                nbin=100
            else:
                nbin=binVar[1]
            if len(binVar)<3:
                min = np.percentile(binVal,1)
                max = np.percentile(binVal,99)
            else:
                min = binVar[2]
                max = binVar[3]
            if isinstance(nbin, int):
                binPoints = np.linspace(min,max,nbin)
            elif isinstance(nbin, float):
                binPoints = np.arange(min,max,nbin)
            binIdx = np.digitize(binVal[FilterOn], binPoints)

            indOn2d = np.ravel_multi_index((scanOnIdx, binIdx),(scanPoints.shape[0]+1, binPoints.shape[0]+1)) 

            # calculate the normalized intensity for each bin
            iNorm = np.bincount(indOn2d, weights=i0Val[FilterOn], minlength=(scanPoints.shape[0]+1)*(binPoints.shape[0]+1)).reshape(scanPoints.shape[0]+1, binPoints.shape[0]+1)    
            iSig = np.bincount(indOn2d, weights=sigVal[FilterOn], minlength=(scanPoints.shape[0]+1)*(binPoints.shape[0]+1)).reshape(scanPoints.shape[0]+1, binPoints.shape[0]+1)    
        else:
            iNorm = np.bincount(scanOnIdx, i0Val[FilterOn])
            iSig = np.bincount(scanOnIdx, sigVal[FilterOn])

        print 'evts ',np.bincount(scanOnIdx)
        print 'i0',iNorm
        print 'sig',iSig
        scan = iSig/iNorm
        #scan = scan/np.mean(scan[1]) # normalize to 1 for first energy point?

        if OffData:
            #same for off shots
            iNormoff = np.bincount(scanOffIdx, i0Val[FilterOff])
            iSigoff = np.bincount(scanOffIdx, sigVal[FilterOff])
            scanoff = iSigoff/iNormoff
        if (not OffData):
            plotDiff = False
        #now save data if desired
        if OffData:
            if saveData:
                np.savetxt('Scan_Run%i.txt'%self.run, (scanPoints, scan, scanOffPoints,scanoff))
            returnDict= {'scanVarName':scanVarName,'scanPoints':scanPoints,'scan':scan, 'scanOffPoints':scanOffPoints,'scanOff':scanoff,'plotVarName':plotVar}
        else:
            if saveData:
                np.savetxt('Scan_Run%i.txt'%self.run, (scanPoints, scan))
            returnDict= {'scanVarName':scanVarName,'scanPoints':scanPoints,'scan':scan,'plotVarName':plotVar}
        if binVar is not None:
            returnDict['binPoints']=binPoints
        if plotThis:
            print 'retData: ',returnDict
            self.plotScanDict(returnDict, plotDiff=plotDiff, interpolation=interpolation,fig=fig,plotOff=plotOff,saveFig=saveFig)
        return returnDict

    def plotScanDict(self, returnDict, plotDiff=True, fig=None, plotOff=True, interpolation='', saveFig=False):
        plotVarName = returnDict['plotVarName']
        scanVarName = returnDict['scanVarName']
        scanPoints = returnDict['scanPoints']
        scan = returnDict['scan']
        print 'plot ',plotVarName, scanVarName, ' shape ',scan.shape

        if interpolation!='' and returnDict.has_key('scanOffPoints'):
            finter_off = interpolate.interp1d(returnDict['scanOffPoints'], returnDict['scanOff'],kind=interpolation)
            scanoff_interp = finter_off(scanPoints[:-1])
        if len(scan.shape)>1:
            if fig is None:
                fig=plt.figure(figsize=(10,5))
            extent = [scanPoints.min(), scanPoints.max(), returnDict['binPoints'].min(), returnDict['binPoints'].max()]
            plt.imshow(scan, interpolation='none', aspect='auto', clim=[np.nanpercentile(scan,1), np.nanpercentile(scan,98)],extent=extent, origin='lower')
            plt.xlabel(scanVarName)
        elif plotDiff and interpolation!='' and returnDict.has_key('scanOffPoints'):
            if fig is None:
                fig=plt.figure(figsize=(10,10))
            gs=gridspec.GridSpec(2,1,width_ratios=[1])
            fig = plt.subplot(gs[0])
            plt.xlabel(scanVarName)
            plt.ylabel(plotVarName)
            fig.plot(scanPoints, scan, 'ro--', markersize=5)
            if interpolation!='':
                fig.plot(scanPoints[:-1], scanoff_interp, 'o--', markersize=5,markerfacecolor='none',markeredgecolor='b')
            fig.plot(returnDict['scanOffPoints'], returnDict['scanOff'], 'ko--', markersize=5)
            plt.ylim(np.nanmin(scan)*0.95,np.nanmax(scan)*1.05)
            fig1 = plt.subplot(gs[1])
            fig1.plot(scanPoints[:-1], (scan[:-1]-scanoff_interp), 'bo--', markersize=5)
            plt.xlabel(scanVarName)
            plt.ylabel(plotVarName)
        else:
            if fig is None:
                fig=plt.figure(figsize=(10,5))
            plt.plot(scanPoints, scan, 'ro--', markersize=5)
            plt.xlabel(scanVarName)
            plt.ylabel(plotVarName)
            if returnDict.has_key('scanOffPoints') and plotOff:
                if interpolation!='':
                    plt.plot(scanPoints[:-1], (scanoff_interp), 'o--', markersize=5,markerfacecolor='none',markeredgecolor='b')
                plt.plot(returnDict['scanOffPoints'], returnDict['scanOff'], 'ko--', markersize=5)
            plt.ylim(np.nanmin(scan)*0.95,np.nanmax(scan)*1.05)
            plt.xlabel(scanVarName)
            plt.ylabel(plotVarName)
        if saveFig:
            fig.savefig('Scan_Run%i.jpg'%self.run)
            
    def defPlots(self, applyCuts=None):
        scanVarName,scan =  self.getScanValues(True)
        total_filter = np.ones_like(scan).astype(bool)
        if applyCuts is not None and self.Sels.has_key(applyCuts):
            total_filter =  self.getFilter(applyCuts, [plotvar])

        fig=plt.figure(figsize=(10,6))
        plt.title('Standard Plots for Run %i'%self.run)
        
        gs=gridspec.GridSpec(2,2,width_ratios=[2,2])
        self.plotVar('ipm2/sum',fig=plt.subplot(gs[0]),applyCuts=applyCuts)
        self.plotVar(['ipm2/sum','ebeam/L3Energy'],fig=plt.subplot(gs[1]),asHist=True,applyCuts=applyCuts)
        if len(scan)<200:
            pmin=scan[0]
            pmax=scan[-1]
        else:
            pmin = np.percentile(scan[total_filter],0.1)
            pmax = np.percentile(scan[total_filter],99.9)
        hst = np.histogram(scan[total_filter],np.linspace(pmin,pmax,100))
        plt.subplot(gs[2]).plot(hst[1][:-1],hst[0],'o')
        #plt.subplot(gs[2]).xlabel(scanVarName)
        #plt.subplot(gs[2]).ylabel('entries')
        plt.xlabel(scanVarName)
        plt.ylabel('entries')
        
        if self.hasKey(self.ttBaseStr+'AMPL'):
            if self.ttCorr is not None and np.nanstd(self.fh5[self.ttCorr].value)>0:
                self.plotVar(self.ttCorr,fig=plt.subplot(gs[3]))
            else:
                self.plotVar(self.ttBaseStr+'FLTPOS_PS',fig=plt.subplot(gs[3]))

    #########################################################
    ###
    ### functions for easy cube creation
    ###
    #########################################################

    #cube might be better to be its own class
    def addCube(self, binVar, bins, cubeName=None, SelName='def'):    
        self.cubes.append(Cube(binVar, bins, cubeName=cubeName, SelName=SelName))        
        
    def addToCube(self, cubeName, targetVariable):
        for cube in self.cubes:
            if cube.cubeName == cubeName:
                cube.targetVars.append(targetVariable)
 
    def printCubes(self, printDetail=True):
        cubeNames=[]
        if len(self.cubes)>0:
            print 'defined cubes:'
            for cube in self.cubes:
                if printDetail:
                    cube.printCube(self.Sels[cube.SelName])
                else:
                    print cube.cubeName
                cubeNames.append(cube.cubeName)
        return cubeNames

    def getCube(self, cubeName=None):
        for cube in self.cubes:
            if cube.cubeName == cubeName:
                return cube
        
    def makeCubeData(self, cubeName, debug=False, toHdf5=False, replaceNan=False):
        cube = self.getCube(cubeName)
        if not (self.hasKey(cube.binVar) or cube.binVar == 'delay'):
            print 'selection variable not in littleData, cannot make the data for this cube'
            return
        if cube.binVar == 'delay':
            binVar = self.getDelay()
        else:
            binVar = self.get1dVar(cube.binVar)
        print 'binvar: ',cube.binVar,binVar.mean()
        print 'getFiler      : ',cube.SelName
        print '    using cuts: ',self.Sels[cube.SelName].printCuts()
        Filter = self.getFilter(cube.SelName)
        binVar = binVar[Filter]
        if binVar.shape[0] == 0:
            print 'did not select any event, quit now!'
            return

        # create the bins for the cube
        if len(cube.bins)==0:
            scanVarName = ''
            for key in self.fh5['scan'].keys():
                if key.find('var')<0 and key.find('none')<0:
                    scanVarName = key
                    break
            if scanVarName!='':
                print 'no cube.bins as input, we will use the scan variable %s '%scanVarName
            else:
                print 'this run is no scan, will need cube.bins as input, quit now'
                return
            Bins = np.unique(self.fh5['scan/var0'])
        elif len(cube.bins)==1:
            print 'you passed only one number for binning, this is not implemented'
        elif len(cube.bins)==2:
            print 'only two bin boundaries, so this is effectively a cut...cube will have a single image'
            Bins = np.array([min(cube.bins[0],cube.bins[1]),max(cube.bins[0],cube.bins[1])])
        elif len(cube.bins)==3:
            if type(cube.bins[2]) is int:
                Bins=np.linspace(min(cube.bins[0],cube.bins[1]),max(cube.bins[0],cube.bins[1]),cube.bins[2])
            else:
                Bins=np.arange(min(cube.bins[0],cube.bins[1]),max(cube.bins[0],cube.bins[1]),cube.bins[2])
        else:
            Bins = cube.bins

        numBins=len(Bins)+1
        if len(cube.bins)<3:
            numBins=len(Bins)

        if debug:
            print 'bin boundaries: ',Bins
        binNum = np.digitize(binVar, Bins,right=True)
        nEvts_bin = np.bincount(binNum)
        if debug:
            print 'events/bin ',nEvts_bin

        cubes = {'Entries': nEvts_bin}
        for tVar in cube.targetVars:
            if not self.hasKey(tVar):
                continue
            var_binned1d = None
            if replaceNan:
                tVarFilter = np.nan_to_num(self.fh5[tVar].value[Filter])
            else:
                tVarFilter = self.fh5[tVar].value[Filter]

            if len(self.fh5[tVar].shape)==1:
                var_binned = np.bincount(binNum, tVarFilter)
                cubes[tVar] = var_binned
            elif len(self.fh5[tVar].shape)==2:
                var_binned = np.array([ np.bincount(binNum,tVarFilter[:,i]) for i in np.arange(tVarFilter.shape[1]) ])
                var_binned1d = np.bincount(binNum, tVarFilter.squeeze().mean(axis=1))
                cubes[tVar] = var_binned
                cubes[tVar+'_1d'] = var_binned1d
            else:
                var_binned1d = np.bincount(binNum, tVarFilter.squeeze().mean(axis=1).mean(axis=1))
                cubes[tVar+'_1d'] = var_binned1d

                var_bin2d = tVarFilter.squeeze().mean(axis=1)
                var_binned2d = np.array([ np.bincount(binNum,var_bin2d[:,i]) for i in np.arange(var_bin2d.shape[1]) ])
                var_bin2d2 = tVarFilter.squeeze().mean(axis=2)
                var_binned2d2 = np.array([ np.bincount(binNum,var_bin2d2[:,i]) for i in np.arange(var_bin2d2.shape[1]) ])
                cubes[tVar+'_2d_0'] = var_binned2d
                cubes[tVar+'_2d_1'] = var_binned2d2
                arsz = 1; arShape=();nevtSel = tVarFilter.shape[0]
                for sz in tVarFilter.shape[1:]:
                    if [sz != 1]:
                        arsz*=sz
                        arShape+=(sz,)
                arShapeBin=arShape+(numBins,)
                newAr = tVarFilter.reshape(nevtSel, arsz)
                var_binned = np.array([ np.bincount(binNum, newAr[:,i]) for i in np.arange(newAr.shape[1]) ])
                var_binned = var_binned.transpose()
                var_binned = np.array([ binDat.reshape(arShape) for binDat in var_binned])
                cubes[tVar] = var_binned

        if toHdf5:
            fname = 'Cube_%s_Run%03d.h5'%(cubeName, self.run)
            dictToHdf5(fname,cubes)

        return cubes

    def writeCube(self, cubeName=None):
        if cubeName is not None:
            if cubeName in [ cube.cubeName for cube in self.cubes ]:
                f = open('CubeSetup_'+cubeName+'.txt','w')
                print 'write CubeSetup file for ',cubeName, ' to ','CubeSetup_'+cubeName+'.txt'
                if isinstance(cube.bins,list):
                    json.dump([cube.binVar,cube.bins,cube.targetVars,self.Sels[cube.SelName].cuts], f, indent=3)
                else:
                    json.dump([cube.binVar,cube.bins.tolist(),cube.targetVars,self.Sels[cube.SelName].cuts], f, indent=3)
                f.close()
                return
            else:
                print 'no cube with nam %s defined, all options are: '%cubeName
                print self.printCubes()
                return
            cubeName = self.printCubes()
        for cube in self.cubes:
            f = open('CubeSetup_'+cube.cubeName+'.txt','w')
            print 'write CubeSetup file for ',cube.cubeName
            json.dump([cube.binVar,cube.bins.tolist(),cube.targetVars,self.Sels[cube.SelName].cuts], f, indent=3)
            f.close()

    def submitCube(self, cubeName, run=None, expname=None, image=False, rebin=-1):                                    
        if socket.gethostname().find('psana')<0:
            print 'we can only submit jobs from psana, you are on ',socket.gethostname()
            return

        if expname == None:
            expname = self.expname
        if run == None:
            run = self.run
            
        #check if cube file exists
        haveFile = True
        if not path.isfile('CubeSetup_'+cubeName+'.txt'):
            haveFile=False
            for cube in self.cubes:
                if cube.cubeName == cubeName:
                    if raw_input('this cube has not been written yet, do it?(y/n)') == 'y':
                        self.writeCubeSetup(cubeName)
                        haveFile=True
        if not haveFile:
            print 'cube %s has not been defined yet'%cubeName
            return

        if path.isfile('./cubeRun'):
            cmd = './cubeRun -r %i -e %s -c %s'%(run, expname, 'CubeSetup_'+cubeName+'.txt')
        else:
            cmd = '/reg/d/psdm/xpp/%s/res/littleData/xppmodules/scripts/cubeRun -r %i -e %s -c %s'%(expname, run, expname, 'CubeSetup_'+cubeName+'.txt')
        if image:
            cmd+=' -i'
        if rebin>0:
            cmd+=' -R %i'%rebin
        print 'command is: %s'%cmd
        sout = subprocess.check_output([cmd],shell=True)
        print 'and submission returned %s'%sout
        self.jobIds.append(sout.split('Job <')[1].split('> is')[0])

    def checkJobs(self):
        remainingIds=[]
        cmd = "bjobs | awk {'print $1'} | grep -v JOBID | grep -v psana"
        cout = subprocess.check_output([cmd],shell=True)
        print cout
        for jobid in self.jobIds:
            if cout.find(jobid)>=0:
                remainingIds.append(jobid)
            else:
                print 'Job %s is done'%jobid
        self.jobIds = remainingIds

    ##########################################################################
    ###
    ### functions for image treatment - starting w/ assembled 2-d image
    ###
    ##########################################################################

    def AvImage(self, detname='None', numEvts=100, nSkip=0, thresADU=0., thresRms=0.,applyCuts=None, mean=False, std=False):
        #look for detector
        if detname=='None':
            aliases=self.Keys2d()
            if len(aliases)<1:
                print 'no area detectors in littleData, all keys present are:'
                self.Keys(printKeys=True)
            if len(aliases)==1:
                detname = aliases[0]
            else:
                print 'detectors in event: \n',
                for alias in aliases:
                    print alias
                detname = raw_input("Select detector to select ROI of?:\n")
        print 'we are looking at ',detname

        #arrays useful for thresholding
        detsrc = detname.split('/')[0]
        roi = self.fh5['UserDataCfg/%s_bound'%(detname.replace('/','_'))].value
        try:
            rmsFull = self.fh5['UserDataCfg/%s_rms'%detsrc].value
            maskFull = self.fh5['UserDataCfg/%s_mask'%detsrc].value
            rms = rmsFull[roi[0,0]:roi[0,1], roi[1,0]:roi[1,1], roi[2,0]:roi[2,1]].squeeze()
            mask = maskFull[roi[0,0]:roi[0,1], roi[1,0]:roi[1,1], roi[2,0]:roi[2,1]].squeeze()
        except:
            rms=None
            mask = None

        #only events requested
        if applyCuts is not None:
            Filter = self.getFilter(SelName=applyCuts)
            dataAr = self.fh5[detname][Filter,:]
            #dataAr = self.fh5[detname].value.squeeze()[Filter]
            dataAr = dataAr[nSkip:min(nSkip+numEvts, dataAr.shape[0])].squeeze()
        else:
            #now look at subarray
            dataAr = self.fh5[detname][nSkip:min(nSkip+numEvts, self.fh5[detname].shape[0])].squeeze()

        #now apply threshold is requested:
        data='AvImg_'
        if std:
            thresDat = dataAr.mean(axis=0)
            data+='std_'
        elif mean:
            thresDat = dataAr.std(axis=0)
            data+='mean_'
        else:
            thresDat = np.zeros_like(dataAr[0])
            for shot in dataAr:
                if thresADU != 0:
                    shot[shot<abs(thresADU)]=0
                    #shot[shot>=abs(thresADU)]=1
                if thresRms > 0 and rms is not None:
                    shot[shot<thresRms*rms]=0
                    #shot[shot>=thresRms*rms]=1
                thresDat += shot

        if thresADU!=0:
            data+='thresADU%d_'%int(thresADU)
        if thresRms!=0:
            data+='thresRms%d_'%int(thresRms)
        data+=detname.replace('/','_')
        self.__dict__[data]=thresDat
        
    def getAvImage(self,detname=None, ROI=[]):
        avImages=[]
        for key in self.__dict__.keys():
            if key.find('AvImg')>=0:
                if detname is not None and key.find(detname)>=0:
                    avImages.append(key)
                elif detname is None:
                    avImages.append(key)
        if len(avImages)==0:
            print 'creating the AvImage first!'
            return
        elif len(avImages)>1:
            print 'we have the following options: ',avImages
            avImage=raw_input('type the name of the AvImage to use:')
        else:
            avImage=avImages[0]
        detname = avImage.replace('AvImg_','')
        img = self.__dict__[avImage]
        return img
        
    def plotAvImage(self,detname=None, ROI=[],limits=[5,99.5]):
        img = self.getAvImage(detname=detname, ROI=ROI)
        print img.shape

        plotMax = np.percentile(img, limits[1])
        plotMin = np.percentile(img, limits[0])
        print 'using the percentiles %g/%g as plot min/max: (%g, %g)'%(limits[0],limits[1],plotMin,plotMax)

        image = img
        
        fig=plt.figure(figsize=(10,6))
        if ROI!=[]:
            gs=gridspec.GridSpec(1,2,width_ratios=[2,1])        
            plt.subplot(gs[1]).imshow(img[ROI[0][0],ROI[1][0]:ROI[1][1],ROI[2][0]:ROI[2][1]],clim=[plotMin,plotMax],interpolation='None')
        else:
            gs=gridspec.GridSpec(1,2,width_ratios=[99,1])        
        plt.subplot(gs[0]).imshow(image,clim=[plotMin,plotMax],interpolation='None')

        plt.show()
        
    def getPeakAvImage(self,detname=None, ROI=[]):
        img=self.getAvImage(detname=detname, ROI=ROI)
        return [img.max(), img.mean(axis=0).argmax(),img.mean(axis=1).argmax()]

    def FitCircle(self, detname=None, mask=None, method=None, thres=None):
        try:
            from utilities import fitCircle
        except:
            print 'could not import underlying code, this does not work yet'
            return
        print 'nearly done, but there is an issue in the image display and x/y coordinates that needs figuring out with faster x-respose.....'
        #return
        avImages=[]
        for key in self.__dict__.keys():
            if key.find('AvImg')>=0:
                if detname is not None and key.find(detname)>=0:
                    avImages.append(key)
                elif detname is None:
                    avImages.append(key)
        if len(avImages)==0:
            print 'please create the AvImage first!'
            return
        elif len(avImages)>1:
            print 'we have the following options: ',avImages
            avImage=raw_input('type the name of the AvImage to use:')
        else:
            avImage=avImages[0]
        detname = avImage.split('_')[1]
        print 'detname: ',detname,avImage
        image = self.__dict__[avImage]
        if len(image.shape)!=2:
            print 'not a 2-d image! Will return. image %s has %d dims'%(avImage,len(image.shape))
            return

        plotMax = np.percentile(image, 99.5)
        plotMin = np.percentile(image, 5)
        print 'using the 5/99.5% as plot min/max: (',plotMin,',',plotMax,')'

        if mask:
            image = (image*mask)

        #get x & y array from data to get extent
        x = self.fh5['UserDataCfg/%s_x'%detname].value
        y = self.fh5['UserDataCfg/%s_y'%detname].value
        #get the ROI bounds
        if len(avImage.split('_'))>2:
            roiname = avImage.split('_')[2]
            ROI = self.fh5['UserDataCfg/%s_%s_bound'%(detname,roiname)].value
            if len(ROI)==2:
                x = x[ROI[0,0]:ROI[0,1], ROI[1,0]:ROI[1,1]].squeeze()
                y = y[ROI[0,0]:ROI[0,1], ROI[1,0]:ROI[1,1]].squeeze()
            elif len(ROI)==3:
                x = x[ROI[0,0]:ROI[0,1], ROI[1,0]:ROI[1,1], ROI[2,0]:ROI[2,1]].squeeze()
                y = y[ROI[0,0]:ROI[0,1], ROI[1,0]:ROI[1,1], ROI[2,0]:ROI[2,1]].squeeze()
        extent=[x.min(), x.max(), y.min(), y.max()]

        fig=plt.figure(figsize=(10,10))
        plt.imshow(image,extent=extent,clim=[plotMin,plotMax],interpolation='None',aspect='auto')

        if method == None:
            method=raw_input("Select circle points by mouse or threshold [m/t]?:\n")
        if method not in ["m","t"]:
            method=raw_input("Please select m or p (mouse/threshold) or we will return\n")
            if method not in ["m","t"]:
                return

        if method=="m":
            happy = False
            while not happy:
                points=ginput(n=0)
                parr=np.array(points)
                #res: xc, yc, R, residu
                res = fitCircle(parr[:,0],parr[:,1])
                #draw the circle.
                circle = plt.Circle((res[0],res[1]),res[2],color='b',fill=False)
                plt.gca().add_artist(circle)
                plt.plot([res[0],res[0]],[y.min(),y.max()],'r')
                plt.plot([x.min(),x.max()],[res[1],res[1]],'r')

                if raw_input("Happy with this fit:\n") in ["y","Y"]:
                    happy = True
                print 'x,y: ',res[0],res[1],' R ',res[2]
                print 'avs: ',parr[:,0].mean(),parr[:,1].mean()
        else:
            happy = False
            while not happy:
                if thres is None:
                    thres = raw_input("percentile in % of selected points min[,max]:\n")
                if thres.find(',')>=0:
                    thresMin=float(thres.split(',')[0])
                    thresMax=np.percentile(image, float(thres.split(',')[1]))
                else:
                    thresMin=float(thres.split(',')[0])
                    thresMax=np.nanmax(image)
                thresP = np.percentile(image, float(thresMin))
                print 'thresP',thresP
                imageThres=image.copy()
                imageThres[image>thresP]=1
                imageThres[image<thresP]=0
                imageThres[image>thresMax]=0
                fig=plt.figure(figsize=(5,5))
                plt.imshow(imageThres,clim=[-0.1,1.1],extent=extent,aspect='auto')
                if thres is None:
                    if raw_input("Happy with this threshold (y/n):\n") in ["y","Y"]:
                        happy=True
                else:
                    happy=True

            #res = fitCircle(x.flatten()[image.flatten()>thresP],y.flatten()[image.flatten()>thresP])
            res = fitCircle(x.flatten()[imageThres.flatten().astype(bool)],y.flatten()[imageThres.flatten().astype(bool)])
            print 'res',res
            print 'x,y av: ',(x.flatten()[imageThres.flatten().astype(bool)]).mean(),(y.flatten()[imageThres.flatten().astype(bool)].mean())
            circleM = plt.Circle((res[0],res[1]),res[2],color='b',fill=False)
            fig=plt.figure(figsize=(10,10))
            #will need to check of rotation necessary here???
            #plt.imshow(np.rot90(image),extent=extent,clim=[plotMin,plotMax],interpolation='None')
            plt.imshow(image,extent=extent,clim=[plotMin,plotMax],interpolation='None',aspect='auto')
            plt.gca().add_artist(circleM)
            plt.plot([res[0],res[0]],[y.min(),y.max()],'r')
            plt.plot([x.min(),x.max()],[res[1],res[1]],'r')
            print 'x,y: ',res[0],res[1],' R ',res[2]
    
            plt.show()

    def MakeMask(self, detname=None):
        print ' not yet implemented, exists in LittleDataAna_psana.py'

    def azimuthalBinning(self, detname=None):
        print ' not yet implemented, exists in LittleDataProduced.py, uses code in xppmodules/src. Not sure if good idea'

    ##########################################################################
    ###
    ### functions for droplet analysis
    ###
    ##########################################################################

    def DropletCube(self, applyCuts='', i0='ipm3/sum', rangeAdu=[], rangeX=[], rangeY=[], addName='', returnData=False, writeFile=False):
        data='DropletCube_Run%d_%s'%(self.run,addName)
        if applyCuts!='':
            data+='_'+applyCuts
        self.__dict__[data]=None

        #get basename of droplets
        dkey = [ key for key in self.Keys() if key.find('dropletsAdu')>=0]
        if len(dkey)==0:
            print 'did nt find any droplets in this littleData file: ',self.fh5.filename
            return
        if len(dkey)>1:
            print 'we have the following options: ',dbkey
            basename=raw_input('type the name of the droplets to use:')
        else:
            basename = dkey[0].split('dropletsAdu')[0]

        #get filtered list of events
        i0_all = self.fh5[i0].value
        if applyCuts is not None:
            Filter = self.getFilter(SelName=applyCuts)
        else:
            Filter = np.ones_like(i0_all)


            dataAr = self.fh5[detname][Filter,:]
            #dataAr = self.fh5[detname].value.squeeze()[Filter]
            dataAr = dataAr[nSkip:min(nSkip+numEvts, dataAr.shape[0])].squeeze()
        
        #get sum of i0
        i0_sum = i0_all[Filter].sum().astype(float)

        #get all droplets in selected events, ADU>0
        adu = self.fh5[basename+'dropletsAdu'][Filter,:].flatten()[self.fh5[basename+'dropletsAdu'][Filter,:].flatten()>0]
        x = self.fh5[basename+'dropletsX'][Filter,:].flatten()[self.fh5[basename+'dropletsAdu'][Filter,:].flatten()>0]
        y = self.fh5[basename+'dropletsY'][Filter,:].flatten()[self.fh5[basename+'dropletsAdu'][Filter,:].flatten()>0]
        

        #make 3d histo of ADU, X, Y
        if rangeAdu==[]:
            rangeAdu=[np.percentile(adu,1), np.percentile(adu,99.9)]
        if rangeX==[]:
            rangeX=[np.percentile(x,1), np.percentile(x,99.9)]
        if rangeY==[]:
            rangeY=[np.percentile(y,1), np.percentile(y,99.9)]

        binAdu = np.arange(int(rangeAdu[0]), int(rangeAdu[1])).astype(int)
        binX = np.arange(int(rangeX[0]), int(rangeX[1])).astype(int)
        binY = np.arange(int(rangeY[0]), int(rangeY[1])).astype(int)
            
        indA = np.digitize(adu, binAdu)
        indX = np.digitize(x, binX)
        indY = np.digitize(y, binY)
        ind3d = np.ravel_multi_index((indA, indX, indY),(binAdu.shape[0]+1, binX.shape[0]+1, binY.shape[0]+1)) 
        cube = np.bincount(ind3d, minlength=(binAdu.shape[0]+1)*(binX.shape[0]+1)*(binY.shape[0]+1)).reshape(binAdu.shape[0]+1, binX.shape[0]+1, binY.shape[0]+1)

        returnDict= {'i0_sum':i0_sum, 'binAdu':binAdu.tolist(), 'binX':binX.tolist(), 'binY':binY.tolist(),'cube':cube.tolist()}
        self.__dict__[data]=returnDict        

        if writeFile:
            f = open(data+'.txt','w')
            print 'write DropletCube file for ',data, ' to ',data,'.txt'
            #indent does NOT work here...
            #json.dump(returnDict,f,indent=2)
            json.dump(returnDict,f)
            f.close()

        if returnData:
            return returnDict

