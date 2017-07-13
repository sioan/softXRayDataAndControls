import sys
import os
p = ["./psanamon"]
for pi in p:
  if not (pi in sys.path): sys.path.append(pi)

import time
import numpy as np
import threading
from psana import *
from psutil import ImageHelper, HistHelper, HistOverlayHelper, XYPlotHelper
from psdata import XYPlotData, XYEPlotData
from psplotserver import ServerScript
import ConfigParser
import json
from utilities import *

class AreaDet_OnOffScan(object):
    def __init__(self):
        self.plotserver = ServerScript();
        # removing this line will means that send_data calls will be a no-op
        #self.plotserver.socket_init(port=12323,reset_port=12324, bufsize=10);

        self.roi_sig = ROI_rectangle()
        self.roi_norm = ROI_rectangle()
        self.do_norm = 0
        self.nav_offevents = 1
        self.xray_off_code = 192
        self.laser_off_code = 91
        self.n_roi_sig = 10
        self.filter_limit = 0.1
        self.filter_ipm = 3
        self.debug = 0
        self.read_conf()
        
        self.plotserver.socket_init(port=self.server_port,reset_port=self.reset_port, bufsize=10);
        self.listener_thread = threading.Thread(target=self.plotserver.reset_listener) #, args=(self.plotserver,)
        self.listener_thread.daemon = True
        self.listener_thread.start()

        self.fname = "./xpp_peak_"

        if self.debug > 0:
          print '*** here in new init'

    def read_conf(self):
        config = ConfigParser.RawConfigParser()
        config.read('./xppmodules/src/AreaDet_OnOffScan.cfg')
        self.roi_sig_par = json.loads(config.get('AreaDet_OnOffScan','roi_sig'))
        self.roi_sig = ROI_rectangle(*self.roi_sig_par)
        self.roi_norm_par = json.loads(config.get('AreaDet_OnOffScan','roi_norm'))
        self.roi_norm = ROI_rectangle(*self.roi_norm_par)
        self.nav_offevents = config.getint('AreaDet_OnOffScan','nav_offevents')
        self.do_norm = config.getint('AreaDet_OnOffScan','do_norm')
        self.xray_off_code = config.getint('AreaDet_OnOffScan','xray_off_code')
        self.laser_off_code = config.getint('AreaDet_OnOffScan','laser_off_code')
        self.filter_limit = config.getfloat('AreaDet_OnOffScan','filter_limit')
        self.filter_ipm = config.getfloat('AreaDet_OnOffScan','filter_ipm')

        self.tt_res_ps = config.getfloat('AreaDet_OnOffScan','tt_res_fs')
        self.tt_scanmax_ps = config.getfloat('AreaDet_OnOffScan','tt_scanmax_fs')
        self.tt_scanmin_ps = config.getfloat('AreaDet_OnOffScan','tt_scanmin_fs')

        self.doPlot           = config.getint('AreaDet_OnOffScan','doPlot')
        self.doDiff           = config.getint('AreaDet_OnOffScan','doDiff')

        self.readOldRun       = config.getint('AreaDet_OnOffScan','readOldRun')
        self.debug            = config.getint('AreaDet_OnOffScan','debug')
        
        self.dt = -1.1
        self.this_t = 0

        #average fit results for plot vs time
        self.nav_res           = config.getint('AreaDet_OnOffScan','nav_res')
        #self.av_fitpar=np.zeros(3, dtype=np.float64)

        self.server_port     = config.getint('AreaDet_OnOffScan','server_port')
        self.reset_port      = config.getint('AreaDet_OnOffScan','reset_port')

        self.cs140_roi_sig_2d_sum = np.zeros((self.roi_sig.rmax-self.roi_sig.rmin, self.roi_sig.cmax-self.roi_sig.cmin ))

    def beginjob(self, evt, env):
      if self.debug > 0:
        print '*** here in beginjob'

      self.ctrl = (env.configStore()).get(ControlData.ConfigV3, Source('ProcInfo()'))
      self.ctrlPV_name = (self.ctrl.pvControls()[0]).name()
      self.ctrlPV_startVal = (self.ctrl.pvControls()[0]).value()      
      self.definePlots(self.ctrlPV_name)

      #this should be an array on 3 OnHistos. For now use only only, as enough for Hoffman
      self.OnHisto = OnOffHisto()
      self.OffHisto = OnOffHisto()
      self.OnHisto.setW(self.tt_scanmin_ps, self.tt_scanmax_ps, self.tt_res_ps)
      self.OffHisto.setW(self.tt_scanmin_ps, self.tt_scanmax_ps, self.tt_res_ps)
      
      for stringpart in (env.jobName()).split(':'):
        if stringpart.find('stream') >= 0:
          self.stream = int(stringpart[-1])

      if self.readOldRun > 0:
        if self.stream == 0:
          self.OnHisto.json2histo(self.fname + str(self.readOldRun) + '_on.data')
          self.OffHisto.json2histo(self.fname + str(self.readOldRun) + '_off.data')
        else:
          self.OnHisto.json2histo(self.fname + str(self.readOldRun) + str(self.stream) + '_on.data')
          self.OffHisto.json2histo(self.fname + str(self.readOldRun) + str(self.stream) + '_off.data')
          #copyhisto = OnOffHisto()
          #copyhisto.setW(self.tt_scanmin_ps, self.tt_scanmax_ps, self.tt_res_ps)
          #for i in range(1,6):
          #  copyhisto.json2histo(self.fname + str(self.readOldRun) + str(i) + '_on.data')
          #  self.OnHisto.addHisto(copyhisto)
          #  copyhisto.json2histo(self.fname + str(self.readOldRun) + str(i) + '_off.data')
          #  self.OffHisto.addHisto(copyhisto)
            
      print self.OnHisto.nent

      self.fname += str(evt.run())

    def beginrun(self, evt, env):
      if self.debug > 0:
        print 'n_roi ',self.n_roi_sig
        print 'found run number',evt.run()
                          
      #########################
        
      #self.ctrl = (env.configStore()).get(ControlData.ConfigV1, Source('ProcInfo()'))
      self.ctrl = (env.configStore()).get(ControlData.ConfigV3, Source('ProcInfo()'))
      self.ctrlPV_name = (self.ctrl.pvControls()[0]).name()
      self.ctrlPV_startVal = (self.ctrl.pvControls()[0]).value()      

      self.ctrl_vals = np.zeros(100)
      self.ctrl_val = 0
      self.ctrl_name = ''
      if self.debug > 0:
        print 'CTRL ?: ',self.ctrl
      self.ncalib = 0

      self.av_on = np.float64(0)
      self.av_off = np.float64(0)
      self.onVals = np.zeros((100,3),dtype=np.float64)
      self.offVals = np.zeros((100,3),dtype=np.float64)
      self.diffVals = np.zeros((100,3),dtype=np.float64)
      
        
    def begincalibcycle(self, evt, env):

      if self.debug > 0:
        print '*** here in begincalib'

      self.n_laser_on_shots  = 0
      self.n_laser_off_shots = 0
      
      self.counter = 0
      self.my_stepsc=[]
      
      self.laser_on  = 0.
      self.laser_off = 0.
      self.laser_onR  = 0.
      self.laser_offR = 0.
      self.laser_onM  = 0.
      self.laser_offM = 0.
                        
      #print env.keys()
      #print '-------------------------------'
      #print evt.keys()
      stp_ctrl = (env.configStore()).get(ControlData.ConfigV3, Source('ProcInfo()'))
      if stp_ctrl is not None:
        if self.debug > 0:
          print '***  have step ctrl object '
        self.ctrl_val = (stp_ctrl.pvControls()[0]).value()
        if self.ctrl_name == '':
          self.ctrl_name = (stp_ctrl.pvControls()[0]).name()
        if "xt" in self.ctrl_name and np.fabs(self.ctrl_val) < 1e-7:
          self.ctrl_val *= 1e12
        #if self.debug > 0:
        print "*** calibcycle ",self.ncalib," ---  ",self.ctrl_name," ---  ",self.ctrl_val
        if self.ncalib == 0:
          if self.debug > 0:
            print 'OnHisto nent:  ',self.OnHisto.nent
            print 'OnHisto val:   ',self.OnHisto.yval
            print 'OffHist nent:  ',self.OffHisto.nent
            print 'OffHisto val:  ',self.OffHisto.yval
                    
      #if self.ctrl is not None:
      self.ncalib += 1
      self.this_t_str = '%.2f'%(self.this_t)

    def event(self, evt, env):
      #if self.counter%500 == 0 :
      #  print 'event: ',self.counter

      xfel_status = 0
      EVR_code = evt.get(EvrData.DataV3, Source('DetInfo(NoDetector.0:Evr.0)'))
      if EVR_code is None:
        print '** no evr'
        return
      xfel_status, laser_status = pumpprobe_status(EVR_code, [self.xray_off_code], [self.laser_off_code])
      #print 'STATUS: ',xfel_status,' -- ', laser_status

      if (xfel_status == 0):
        return
        
      #plot some events
      evt_data = evt.get(EventId)
      evt_ts = evt_data.time()
      # convert the ts
      evt_ts_str = '%.4f'%(evt_ts[0] + evt_ts[1] / 1e9)
      if self.dt < 0:
        self.dt = evt_ts[0]+int(evt_ts[1]/1e6)*0.001
      else:
        self.this_t =  evt_ts[0]+int(evt_ts[1]/1e6)*0.001 - self.dt
      
      ipm2 = evt.get(Lusi.IpmFexV1, Source('BldInfo(XppSb2_Ipm)')).sum()
      ipm3 = evt.get(Lusi.IpmFexV1, Source('BldInfo(XppSb3_Ipm)')).sum()
      ipmU0 = evt.get(Lusi.IpmFexV1, Source('BldInfo(XppEnds_Ipm0)')).channel()[2]
      ipmU1 = evt.get(Lusi.IpmFexV1, Source('BldInfo(XppEnds_Ipm0)')).channel()[1]

      #use chopper rather than delay w/ evt codes 90 & 91
      if ipmU1 < 1:
        laser_status = 0

      norm = 1
      if self.do_norm == 1 and ipmU0 != 0:
        norm = 1./ipmU0
      if self.do_norm == 2 and ipm2 != 0:
        norm = 1./ipm2
      if self.do_norm == 3 and ipm3 != 0:
        norm = 1./ipm3

      if self.filter_ipm == 1 and ipmU0 < self.filter_limit:
        return
      if self.filter_ipm == 2 and ipm2 < self.filter_limit:
        return
      if self.filter_ipm == 3 and ipm3 < self.filter_limit:
        return

      if (env.epicsStore()).value("TTSPEC:FLTPOS_PS") is not None:
        scanval = self.ctrl_val + (env.epicsStore()).value("TTSPEC:FLTPOS_PS")
      else:
        scanval = self.ctrl_val
        
      #now dealing with the cspad image....

      cspadsrc = 'DetInfo(XppGon.0:Cspad2x2.0)'
      #frame = evt.get(CsPad2x2.ElementV1, Source(cspadsrc))
      #frame = evt.get(CsPad2x2.ElementV1, Source(cspadsrc), "calibrated")
      #image = ImageHelper(self.plotserver.send_data,'cs140_0')
      #image.set_image(frame.data()[:,:,0], evt_ts_str)
      #image.publish()

      #image1 = ImageHelper(self.plotserver.send_data,'cs140_1')
      #image1.set_image(frame.data()[:,:,1], evt_ts_str)
      #image1.publish()

      #present reading
      #frame_data = frame.data()[:,:,0]

      frame = evt.get(ndarray_int16_2, Source(cspadsrc), "reconstructed")
      if frame is None:
        print '** no frame'
        return

      plt.figure('CSPad',figsize(8,8))
      plt.ion()
      plt.show()
      plt.imshow(frame)
      plt.title('CsPad raw: %d', scanval)
      plt.draw()
      #plt.clf()
      
      #self.av_on = update_average(self.nav_res,  self.av_on, np.float64(las_on))
        

      las_on = np.float64(0)
      las_off = np.float64(0)
      las_onM = np.float64(0)
      las_offM = np.float64(0)
      las_onR = np.float64(0)
      las_offR = np.float64(0)
      if (laser_status == 1):
        self.n_laser_on_shots += 1
        if self.doDiff:
          las_on = (cs140_roi_sig - cs140_roi_norm) * norm
        else:
          las_on = cs140_roi_sig * norm
        self.av_on = update_average(self.nav_res,  self.av_on, np.float64(las_on))
        self.laser_on += las_on
        self.on_time.add(self.this_t, las_on, evt_ts_str)
        self.on_time.publish()
        self.onav_time.add(self.this_t, self.av_on, evt_ts_str)
        self.onav_time.publish()
        self.OnHisto.add(scanval, las_on)
      else:
        self.n_laser_off_shots += 1
        if self.doDiff:
          las_off = (cs140_roi_sig - cs140_roi_norm) * norm
        else:
          las_off = cs140_roi_sig * norm
        self.av_off = update_average(self.nav_res, self.av_off, np.float64(las_off))
        self.laser_off += las_off
        self.off_time.add(self.this_t, las_off, evt_ts_str)
        self.off_time.publish()
        self.offav_time.add(self.this_t, self.av_off, evt_ts_str)
        self.offav_time.publish()
        self.OffHisto.add(scanval, las_off)
        
      self.diffav_time.add(self.this_t, (self.av_on - self.av_off)/(self.av_on + self.av_off), evt_ts_str)
      self.diffav_time.publish()
              
      self.counter += 1
      self.checkResetPlots()

    def endcalibcycle(self, evt, env):
      #if self.debug > 0:
      #print '*** here in endcalib'
      if self.ctrl is not None:

        if self.doPlot:
          if self.debug > 0:
            print '*** here in endcalib -- filling the plots'
          if self.n_laser_on_shots > 0:
            self.on_calib.add(self.ctrl_val, self.laser_on / self.n_laser_on_shots, self.this_t_str)
          if self.n_laser_off_shots > 0:
            self.off_calib.add(self.ctrl_val, self.laser_off / self.n_laser_off_shots, self.this_t_str)
          if self.n_laser_on_shots > 0 and self.n_laser_off_shots > 0:
            reldiff = self.laser_on / self.n_laser_on_shots - self.laser_off / self.n_laser_off_shots
            reldiff = reldiff / (self.laser_on / self.n_laser_on_shots + self.laser_off / self.n_laser_off_shots)
            self.diff_calib.add(self.ctrl_val, reldiff, self.this_t_str)
          self.on_calib.publish()
          self.off_calib.publish()
          self.diff_calib.publish()
              
          #print 'self.ncalib ',self.ncalib
          self.ctrl_vals[self.ncalib-1] = self.ctrl_val
          if self.n_laser_off_shots > 0:
            self.offVals[self.ncalib-1][0] = self.laser_off / self.n_laser_off_shots
          if self.n_laser_on_shots > 0:
            self.onVals[self.ncalib-1][0] = self.laser_on / self.n_laser_on_shots
          if self.n_laser_on_shots > 0 and self.n_laser_off_shots > 0:
            reldiff = self.laser_on / self.n_laser_on_shots - self.laser_off / self.n_laser_off_shots
            reldiff = reldiff / (self.laser_on / self.n_laser_on_shots + self.laser_off / self.n_laser_off_shots)
            self.diffVals[self.ncalib-1][0] = reldiff

          calib_onoff = XYPlotData(self.this_t_str, 'calib_onoff', [self.ctrl_vals ,self.ctrl_vals ],[ self.onVals[:,0], self.offVals[:,0]], xlabel=self.ctrlPV_name, ylabel='on off reads', formats='.')
          self.plotserver.send_data('calib_onoff',calib_onoff)
          
          #if self.debug > 0:
          #print "*** calibcycle ",self.ncalib," ---  ",self.ctrl_name," ---  ",self.ctrl_val
            #print '---------------',self.OnHisto.nent
            #print '------XXX------',self.OnHisto.yval
            #print '...............',self.OffHisto.nent
            #print '......XXX......',self.OffHisto.yval
            #print 'onmean: ',self.OnHisto.means()
            #print 'offmean: ',self.OffHisto.means()
          OnOffTT = XYPlotData(self.this_t_str, 'OnOffTT', [self.OnHisto.bin_centers ,self.OffHisto.bin_centers ],[ self.OnHisto.means(), self.OffHisto.means()], xlabel=(self.ctrlPV_name+'_ttcorr'), ylabel='on ', formats='.')
          self.plotserver.send_data('OnOffTT',OnOffTT)

          DiffTT = XYPlotData(self.this_t_str, 'DiffTT', self.OnHisto.bin_centers, (self.OnHisto.means()-self.OffHisto.means())/(self.OnHisto.means()+self.OffHisto.means()), xlabel=self.ctrlPV_name+'_ttcorr', ylabel='diff ', formats='.')
          self.plotserver.send_data('DiffTT',DiffTT)

          xerr = np.zeros(self.OnHisto.nbins)
          OnETT = XYEPlotData(self.this_t_str, 'OnETT', self.OnHisto.bin_centers, self.OnHisto.means(), np.sqrt(self.OnHisto.errSq()), xerr, xlabel=self.ctrlPV_name+'_ttcorr', ylabel='onE ', formats='.')
          self.plotserver.send_data('OnETT',OnETT)

      else:
        res_arr = np.array(self.my_stepsc)

    def endrun(self, evt, env):
      if self.debug > 0:
        print '*** here in endrun'
        print 'OnHisto nent:  ',self.OnHisto.nent
        print 'OnHisto val:   ',self.OnHisto.yval
        print 'OffHist nent:  ',self.OffHisto.nent
        print 'OffHisto val:  ',self.OffHisto.yval

    def endjob(self, evt, env):
      if self.stream > 0:
        self.OnHisto.histo2json(self.fname + '_str' + str(self.stream) + '_on.data')
        self.OffHisto.histo2json(self.fname + '_str' + str(self.stream) +'_off.data')
      else:
        self.OnHisto.histo2json(self.fname+'_on.data')
        self.OffHisto.histo2json(self.fname+'_off.data')

    def definePlots(self, controlPVname='scanVar2'):
      self.plotlist=[]
      self.on_calib = XYPlotHelper(self.plotserver.send_data, 'on_calib', xlabel=controlPVname, ylabel='on', format='.')
      self.plotlist.append(self.on_calib)
      self.off_calib = XYPlotHelper(self.plotserver.send_data, 'off_calib', xlabel=controlPVname, ylabel='off', format='.')
      self.plotlist.append(self.off_calib)
      self.diff_calib = XYPlotHelper(self.plotserver.send_data, 'diff_calib', xlabel=controlPVname, ylabel='diff', format='.')
      self.plotlist.append(self.diff_calib)

      self.on_time = XYPlotHelper(self.plotserver.send_data, 'on_time', xlabel='eventTimeR', ylabel='on', format='.', pubrate=1)
      self.plotlist.append(self.on_time)
      self.off_time = XYPlotHelper(self.plotserver.send_data, 'off_time', xlabel='eventTimeR', ylabel='off', format='.', pubrate=1)
      self.plotlist.append(self.off_time)

      self.onav_time = XYPlotHelper(self.plotserver.send_data, 'onav_time', xlabel='eventTimeR', ylabel='av(on)', format='.', pubrate=1)
      self.plotlist.append(self.onav_time)
      self.offav_time = XYPlotHelper(self.plotserver.send_data, 'offav_time', xlabel='eventTimeR', ylabel='av(off)', format='.', pubrate=1)
      self.plotlist.append(self.offav_time)
      self.diffav_time = XYPlotHelper(self.plotserver.send_data, 'diffav_time', xlabel='eventTimeR', ylabel='av(diff)', format='.', pubrate=1)
      self.plotlist.append(self.diffav_time)


    def checkResetPlots(self):
      if self.plotserver.get_reset_flag():
        print '*** resetting plots'
        for plot in self.plotlist:
          plot.clear()
        self.plotserver.clear_reset_flag()
