#
# add option to prepareImg to mask the direct neighbors of masked pixels as well
# only to be used for default threshold _not_ the lower one.
#
# with two thresholds: re-label w/ second threshold image (optionally)
#
# photonize: store differently: store pos w/ number of photons (not COM for last photon, but pixels)
#
# 'fitting': model distributions of multiple photons in 2,3,4 pixels & compare chi sq to actual data.
#
import numpy as np
import time
import psana

class timetool:
    def __init__(self, useProjection=False, kind='stepDown', weights=None, ttROIs=None, beamOff=None, laserOff=None):
        """ 
        class to extract timetool information from data
        ttROIs are taken from configuration data unless provided as list of lists (signal, sideband, ref [r0, c0, r1, c1])
        kind='stepUp' : 'stepUp' is default for fit. if None, no refitting will be performed
        weights are taken from configuration data unless provided
        beam & laser on/off codes also taken from data unless provided as lists
        actual fitting code from ixppy
        """
        self.kind = kind
        self.weights=weights
        self.ttROI_signal=None
        self.ttROI_sideband=None
        self.ttROI_reference=None
        if ttROIs is not None:
                if len(ttROIs)==4 and isinstance(ttROIs[0], int):
                        self.ttROI_signal=ttROIs
                elif len(ttROIs)>=1:
                        self.ttROI_signal=ttROIs[0]
                        self.ttROI_reference=ttROIs[0]
                        if len(ttROIs)>=2:
                                self.ttROI_sideband=ttROIs[1]
                        if len(ttROIs)>2:
                                self.ttROI_reference=ttROIs[2]
        self.beamOff=beamOff
        self.laserOff=laserOff
        self.debug=False
        self.ttCalib = [ np.nan, np.nan ]
        self.useProjection=useProjection
        self.runningRef=None

    def setDebug(self, debug):
        if isinstance(debug, bool):
                self.debug = debug

    def set_ttCalib(self, calibPars):
      if calibPars != None:
        self.ttCalib = calibPars

    def getConfigFromData(self, env):
        for cfgKey in env.configStore().keys():
            if cfgKey.type() == psana.TimeTool.ConfigV2:
              self.ttAlias=cfgKey.alias()
              
        ttCfg = env.configStore().get(psana.TimeTool.ConfigV2, psana.Source(self.ttAlias))
        self.ttCalib = ttCfg.calib_poly()
        self.ttDet=psana.Detector(self.ttAlias)
        self.ttProj=ttCfg.write_projections()
        self.sb_convergence=ttCfg.sb_convergence()
        self.ref_convergence=ttCfg.ref_convergence()
        self.subtract_sideband=ttCfg.subtract_sideband()
        if self.ttROI_signal is None:
                    self.ttROI_signal = [[ttCfg.sig_roi_lo().row(),ttCfg.sig_roi_hi().row()],\
                                         [ttCfg.sig_roi_lo().column(),ttCfg.sig_roi_hi().column()]]
        if self.ttROI_sideband is None:
                    self.ttROI_sideband = [[ttCfg.sb_roi_lo().row(),ttCfg.sb_roi_hi().row()],\
                                           [ttCfg.sb_roi_lo().column(),ttCfg.sb_roi_hi().column()]]
        if self.ttROI_reference is None:
                    if ttCfg.use_reference_roi()>0:
                        self.ttROI_reference = [[ttCfg.ref_roi_lo().row(),ttCfg.ref_roi_hi().row()],\
                                                [ttCfg.ref_roi_lo().column(),ttCfg.ref_roi_hi().column()]]
                    else:
                        self.ttROI_reference = self.ttROI_signal

        if self.weights is None:
                self.weights = ttCfg.weights()
                
        if self.beamOff is None:
                self.beamOff=[]
                for el in ttCfg.beam_logic():
                        self.beamOff.append(el.event_code())
        if self.laserOff is None:
                self.laserOff=[]
                for el in ttCfg.laser_logic():
                        self.laserOff.append(el.event_code())

        self.runningRef=None

    def setRunningRef(self, refData):
        self.runningRef=refData

    def getTraces(self, evt):
        #check that we have reference, otherwise replace by none
        ec=[]
        evrData = evt.get(psana.EvrData.DataV4, psana.Source('evr0'))
        ts_40=0
        for fevt in evrData.fifoEvents(): 
            if fevt.eventCode()==40:
                ts_40=fevt.timestampHigh()
        for fevt in evrData.fifoEvents(): 
                if fevt.timestampHigh() == ts_40:
                        ec.append(fevt.eventCode())

        ttDet=evt.get(psana.TimeTool.DataV2, psana.Source(self.ttAlias))
        ttData={}
        if self.ttROI_sideband is not None:
            ttData['tt_sideband']=np.zeros(abs(self.ttROI_sideband[0][0]-self.ttROI_sideband[0][1]))
        ttData['tt_signal']=np.zeros(abs(self.ttROI_signal[0][0]-self.ttROI_signal[0][1]))
        if self.ttROI_signal is not None:
            ttData['tt_reference']=self.runningRef
        for lOff in self.laserOff:
            if lOff in ec:
                return ttData
            
        try:
            ttData['tt_signal_pj']=ttDet.projected_signal().astype(dtype='uint32').astype(float)
            ttData['tt_sideband_pj']=ttDet.projected_sideband().astype(dtype='uint32').astype(float)
            ttData['tt_reference_pj']=ttDet.projected_reference().astype(dtype='uint32').astype(float)
            ttImg = self.ttDet.raw(evt)
            if self.ttROI_signal is not None:
                ttData['tt_signal']=ttImg[self.ttROI_signal[0][0]:self.ttROI_signal[0][1],self.ttROI_signal[1][0]:self.ttROI_signal[1][1]].mean(axis=0)          
            if self.ttROI_sideband is not None:
                ttData['tt_sideband']=ttImg[self.ttROI_sideband[0][0]:self.ttROI_sideband[0][1],self.ttROI_sideband[1][0]:self.ttROI_sideband[1][1]].mean(axis=0)
            if self.ttROI_reference is not None:
                beamOff=False
                for bOff in self.beamOff:
                    if bOff in ec:
                        beamOff=True
                if beamOff:
                    ttRef = ttImg[self.ttROI_reference[0][0]:self.ttROI_reference[0][1],self.ttROI_reference[1][0]:self.ttROI_reference[1][1]].mean(axis=0)
                    if self.runningRef is None:
                        self.runningRef=ttRef
                    else:
                        print 'have running ref!',self.ref_convergence, self.runningRef[10], ttRef[10]
                        self.runningRef=ttRef*self.ref_convergence + self.runningRef*(1.-self.ref_convergence)
                    print 'have updated self.runningRef'
                ttData['tt_reference']=self.runningRef
        except:
            pass
        
        return ttData

    def prepareTrace(self, evt):
        ttData = self.getTraces(evt)
        if len(ttData.keys())==0:
            return None

        if self.useProjection:
            ttRef=ttData['tt_reference_pj']
            ttSignal=ttData['tt_signal_pj']
            if self.subtract_sideband>0:
                ttSignal-=ttData['tt_sideband_pj']
                ttRef-=ttData['tt_sideband_pj']
        else:
            ttRef=ttData['tt_reference'].copy()
            ttSignal=ttData['tt_signal']
            if self.subtract_sideband>0:
                ttSignal-=ttData['tt_sideband']
                ttRef-=ttData['tt_sideband']

        return ttSignal/ttRef

    def fitTrace(self, evt):
        data = self.prepareTrace(evt)
        return self.fitTraceData(data)

    def fitTraceData(self, data):
        if data is None or len(data)<10:
            return
        lf = len(self.weights)
        halfrange = round(lf/10)
        retDict = {}
        retDict['pos']=0.
        retDict['amp']=0.
        retDict['fwhm']=0.
        
        f0 = np.convolve(np.array(self.weights).ravel(),data,'same')
        f = f0[lf/2:len(f0)-lf/2-1]
        retDict['f']=f
        if (self.kind=="stepDown"):
            mpr = f.argmin()
        else:
            mpr = f.argmax()
        # now do a parabolic fit around the max
        xd = np.arange(max(0,mpr-halfrange),min(mpr+halfrange,len(f)-1))
        yd = f[max(0,mpr-halfrange):min(mpr+halfrange,len(f)-1)]
        p2 = np.polyfit(xd,yd,2)
        tpos = -p2[1]/2./p2[0]
        tamp = np.polyval(p2,tpos)
        try:
            if self.kind == 'stepDown':
                beloh = (f>((f[-25:].mean()+tamp)/2.)).nonzero()[0]-mpr
            else:
                beloh = (f<tamp/2).nonzero()[0]-mpr            
            #print 'beloh ',len(beloh[beloh<0]),len(beloh[beloh>0])
            tfwhm = abs(beloh[beloh<0][-1]-beloh[beloh>0][0])
        except:
            tfwhm = 0.
        if self.kind == 'stepDown':
            tamp = abs(f[-25:].mean()-tamp)
        retDict['pos']=tpos + lf/2.
        retDict['amp']=tamp
        retDict['fwhm']=tfwhm
        ttOrg = retDict['pos']
        ttCorr = self.ttCalib[0]+ ttOrg*self.ttCalib[1]
        if len(self.ttCalib)>2:
            ttCorr+=ttOrg*ttOrg*self.ttCalib[2]
        retDict['pos_ps']=ttCorr

        return retDict
            
