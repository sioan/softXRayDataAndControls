import sys
import os
#p = ["/reg/g/xpp/xppcode/python","/reg/g/pcds/pds/pyca"] #"/reg/neh/home1/marcoc/python_modules"]
p = ["/reg/g/xpp/xppcode/python","/reg/g/pcds/pds/pyca","/reg/common/package/python/2.7.2-rhel6/lib/python2.7/site-packages","./psanamon"]
for pi in p:
  if not (pi in sys.path): sys.path.append(pi)

import time
import numpy as np
import threading
from psana import *
from psutil import ImageHelper, HistHelper, HistOverlayHelper, XYPlotHelper
from psdata import XYPlotData
from psplotserver import ServerScript
import ConfigParser
import json
from utilities import *
#only temporarily
import matplotlib.pyplot as plt

#for file in sys.path:
#  print file

#import pyca
#from pyca import Pv as pycaPv
#this requires extra stuff in LD_LIBRARY_PATH, like /reg/g/pcds/package/epics/3.14/base/current/lib/linux-x86 (as well as others)
from Pv import Pv
#from xpp import pypsepics


class xpp_peak(object):
    def __init__(self):
        self.plotserver = ServerScript();
        # removing this line will means that send_data calls will be a no-op
        self.plotserver.socket_init(port=12323,reset_port=12324, bufsize=10);
        self.listener_thread = threading.Thread(target=self.plotserver.reset_listener) #, args=(self.plotserver,)
        self.listener_thread.daemon = True
        self.listener_thread.start()

        print '*** here in new init'
        self.roi_sig = ROI_rectangle()
        self.roi_norm = ROI_rectangle()
        self.do_norm = 0
        self.nav_offevents = 1
        self.xray_off_code = 192
        self.laser_off_code = 91
        self.n_roi_sig = 10
        self.filter_limit = 0.1
        self.filter_ipm = 3
        self.writePV = []
        self.debug = 0
        self.read_conf()
        self.epicsNameIDontUnderstand = ["XPP:USER:NEW:NEW_4_POS"]

    def read_conf(self):
        config = ConfigParser.RawConfigParser()
        config.read('./xppmodules/src/xpp_peak.cfg')
        self.roi_sig_par = json.loads(config.get('xpp_peak','roi_sig'))
        self.roi_sig = ROI_rectangle(*self.roi_sig_par)
        self.roi_sigM_par = json.loads(config.get('xpp_peak','roi_sigM'))
        self.roi_sigM = ROI_rectangle(*self.roi_sigM_par)
        self.roi_sigR_par = json.loads(config.get('xpp_peak','roi_sigR'))
        self.roi_sigR = ROI_rectangle(*self.roi_sigR_par)
        self.roi_norm_par = json.loads(config.get('xpp_peak','roi_norm'))
        self.roi_norm = ROI_rectangle(*self.roi_norm_par)
        self.nav_offevents =  config.getint('xpp_peak','nav_offevents')
        self.do_norm = config.getint('xpp_peak','do_norm')
        self.xray_off_code =  config.getint('xpp_peak','xray_off_code')
        self.laser_off_code =  config.getint('xpp_peak','laser_off_code')
        self.filter_limit =  config.getfloat('xpp_peak','filter_limit')
        self.filter_ipm =  config.getfloat('xpp_peak','filter_ipm')

        self.write_PV         = config.getint('xpp_peak','write_PV')
        self.doFit            = config.getint('xpp_peak','doFit')
        self.doPlot           = config.getint('xpp_peak','doPlot')
        self.doFitPlot        = config.getint('xpp_peak','doFitPlot')
        self.doDiff           = config.getint('xpp_peak','doDiff')
        self.numPixelFit      = config.getint('xpp_peak','numPixelFit')
        self.debug            = config.getint('xpp_peak','debug')
        
        self.dt = -1.1
        self.this_t = 0

        #average fit results for plot vs time
        self.nav_res           = config.getint('xpp_peak','nav_res')
        self.av_fitpar=np.zeros(3, dtype=np.float64)

        self.cs140_roi_sig_2d_sum = np.zeros((self.roi_sig.rmax-self.roi_sig.rmin, self.roi_sig.cmax-self.roi_sig.cmin ))

    def beginjob(self, evt, env):
      if self.debug > 0:
        print '*** here in beginjob'

    def beginrun(self, evt, env):
      if self.debug > 0:
        print 'n_roi ',self.n_roi_sig
        print 'found run number',evt.run()
                          
      if self.write_PV == 1:
        self.Pv01 = Pv("XPP:VARS:FLOAT:04")
        self.Pv02 = Pv("XPP:VARS:FLOAT:05")
        self.Pv03 = Pv("XPP:VARS:FLOAT:06")
        try:
          self.Pv01.connect()
          self.Pv02.connect()
          self.Pv03.connect()
        except:
          print 'cannot write to PVs - probably not on machine with xpp-cds'
          self.write_PV = 0

      #########################
        
      self.epics = env.epicsStore()
      #self.ctrl = (env.configStore()).get(ControlData.ConfigV1, Source('ProcInfo()'))
      self.ctrl = (env.configStore()).get(ControlData.ConfigV3, Source('ProcInfo()'))
      self.ctrlPV_name = (self.ctrl.pvControls()[0]).name()      

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
      
      self.definePlots(self.ctrlPV_name)
        
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
        #if self.debug > 0:
        print "*** calibcycle ",self.ncalib," ---  ",self.ctrl_name," ---  ",self.ctrl_val

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
        
      cspadsrc = 'DetInfo(XppGon.0:Cspad2x2.0)'
      frame = evt.get(CsPad2x2.ElementV1, Source(cspadsrc))
      if frame is None:
        print '** no frame'
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
      

      image = ImageHelper(self.plotserver.send_data,'cs140_0')
      image.set_image(frame.data()[:,:,0], evt_ts_str)
      image.publish()

      image1 = ImageHelper(self.plotserver.send_data,'cs140_1')
      image1.set_image(frame.data()[:,:,1], evt_ts_str)
      image1.publish()

      #present reading
      frame_data = frame.data()[:,:,0]

      #use the ROI_rectable class now.
      cs140_roi_sig_2d = self.roi_sig.select(frame_data)
      imageR = ImageHelper(self.plotserver.send_data,'cs140_sig_roi')
      imageR.set_image(cs140_roi_sig_2d, evt_ts_str)
      imageR.publish()
      self.cs140_roi_sig_2d_sum += cs140_roi_sig_2d
      imageRS = ImageHelper(self.plotserver.send_data,'cs140_sig_roi_sum')
      imageRS.set_image(self.cs140_roi_sig_2d_sum, evt_ts_str)
      imageRS.publish()

      cs140_roi_norm_2d = self.roi_norm.select(frame_data)
      imageRN = ImageHelper(self.plotserver.send_data,'cs140_norm_roi')
      imageRN.set_image(cs140_roi_norm_2d, evt_ts_str)
      imageRN.publish()

      #self.bin_ar = np.arange(self.roi_sig.cmin,self.roi_sig.cmax)
      #cs140_roi_sig = self.roi_sig.projx( frame_data )
      #xysig = XYPlotData(evt_ts_str, 'roi_projx', self.bin_ar, cs140_roi_sig, xlabel='bin#', ylabel='sig')
      #self.plotserver.send_data('roi_projx',xysig)

      #self.bin_ary = np.arange(self.roi_sig.rmin,self.roi_sig.rmax)
      #cs140_roi_sig = self.roi_sig.projy( frame_data )
      #xysig = XYPlotData(evt_ts_str, 'roi_projy', self.bin_ary, cs140_roi_sig, xlabel='bin#', ylabel='sig')
      #self.plotserver.send_data('roi_projy',xysig)

      #print 'sig max: ',self.roi_sig.max( frame_data),' -- sum: ', self.roi_sig.sum( frame_data)

      cs140_roi_sig = self.roi_sig.mean( frame_data )
      cs140_roi_sigM = self.roi_sigM.mean( frame_data )
      cs140_roi_sigR = self.roi_sigR.mean( frame_data )
      #norm of same size for common mode noise subtraction
      cs140_roi_norm = self.roi_norm.mean( frame_data )

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
          las_onM = (cs140_roi_sigM - cs140_roi_norm) * norm
          las_onR = (cs140_roi_sigR - cs140_roi_norm) * norm
        else:
          las_on = cs140_roi_sig * norm
          las_onM = cs140_roi_sigM * norm
          las_onR = cs140_roi_sigR * norm
        self.av_on = update_average(self.nav_res,  self.av_on, np.float64(las_on))
        self.laser_on += las_on
        self.laser_onM += las_onM
        self.laser_onR += las_onR
        self.on_time.add(self.this_t, las_on, evt_ts_str)
        self.on_time.publish()
        self.onav_time.add(self.this_t, self.av_on, evt_ts_str)
        self.onav_time.publish()
      else:
        self.n_laser_off_shots += 1
        if self.doDiff:
          las_off = (cs140_roi_sig - cs140_roi_norm) * norm
          las_offM = (cs140_roi_sigM - cs140_roi_norm) * norm
          las_offR = (cs140_roi_sigR - cs140_roi_norm) * norm
        else:
          las_off = cs140_roi_sig * norm
          las_offM = cs140_roi_sigM * norm
          las_offR = cs140_roi_sigR * norm
        self.av_off = update_average(self.nav_res, self.av_off, np.float64(las_off))
        self.laser_off += las_off
        self.laser_offM += las_offM
        self.laser_offR += las_offR
        self.off_time.add(self.this_t, las_off, evt_ts_str)
        self.off_time.publish()
        self.offav_time.add(self.this_t, self.av_off, evt_ts_str)
        self.offav_time.publish()

      #self.diff_time.add(self.this_t, np.float64(las_on - las_off), evt_ts_str)
      #self.diff_time.publish()
      self.diffav_time.add(self.this_t, self.av_on - self.av_off, evt_ts_str)
      self.diffav_time.publish()
              
      self.counter += 1
      self.checkResetPlots()

    def endcalibcycle(self, evt, env):
      if self.debug > 0:
        print '*** here in endcalib'
      if self.ctrl is not None:

        if self.doPlot:
          if self.debug > 0:
            print '*** here in endcalib -- filling the plots'
          if self.n_laser_on_shots > 0:
            self.on_calib.add(self.ctrl_val, self.laser_on / self.n_laser_on_shots, self.this_t_str)
            self.onM_calib.add(self.ctrl_val, self.laser_onM / self.n_laser_on_shots, self.this_t_str)
            self.onR_calib.add(self.ctrl_val, self.laser_onR / self.n_laser_on_shots, self.this_t_str)
          if self.n_laser_off_shots > 0:
            self.off_calib.add(self.ctrl_val, self.laser_off / self.n_laser_off_shots, self.this_t_str)
            self.offM_calib.add(self.ctrl_val, self.laser_offM / self.n_laser_off_shots, self.this_t_str)
            self.offR_calib.add(self.ctrl_val, self.laser_offR / self.n_laser_off_shots, self.this_t_str)
          if self.n_laser_on_shots > 0 and self.n_laser_off_shots > 0:
            self.diff_calib.add(self.ctrl_val, self.laser_on / self.n_laser_on_shots - self.laser_off / self.n_laser_off_shots, self.this_t_str)
            self.diffM_calib.add(self.ctrl_val, self.laser_onM / self.n_laser_on_shots - self.laser_offM / self.n_laser_off_shots, self.this_t_str)
            self.diffR_calib.add(self.ctrl_val, self.laser_onR / self.n_laser_on_shots - self.laser_offR / self.n_laser_off_shots, self.this_t_str)
          self.on_calib.publish()
          self.off_calib.publish()
          self.diff_calib.publish()
          self.onR_calib.publish()
          self.offR_calib.publish()
          self.diffR_calib.publish()
          self.onM_calib.publish()
          self.offM_calib.publish()
          self.diffM_calib.publish()
              
          #print 'self.ncalib ',self.ncalib
          self.ctrl_vals[self.ncalib-1] = self.ctrl_val
          if self.n_laser_off_shots > 0:
            self.offVals[self.ncalib-1][0] = self.laser_off / self.n_laser_off_shots
            self.offVals[self.ncalib-1][1] = self.laser_offM / self.n_laser_off_shots
            self.offVals[self.ncalib-1][2] = self.laser_offR / self.n_laser_off_shots
          if self.n_laser_on_shots > 0:
            self.onVals[self.ncalib-1][0] = self.laser_on / self.n_laser_on_shots
            self.onVals[self.ncalib-1][1] = self.laser_onM / self.n_laser_on_shots
            self.onVals[self.ncalib-1][2] = self.laser_onR / self.n_laser_on_shots
          if self.n_laser_on_shots > 0 and self.n_laser_off_shots > 0:
            self.diffVals[self.ncalib-1][0] = self.laser_on / self.n_laser_on_shots - self.laser_off / self.n_laser_off_shots
            self.diffVals[self.ncalib-1][1] = self.laser_onM / self.n_laser_on_shots - self.laser_offM / self.n_laser_off_shots
            self.diffVals[self.ncalib-1][2] = self.laser_onR / self.n_laser_on_shots - self.laser_offR / self.n_laser_off_shots
          calib_alloff = XYPlotData(self.this_t_str, 'calib_alloff', [self.ctrl_vals ,self.ctrl_vals ,self.ctrl_vals ],[ self.offVals[:,0], self.offVals[:,1], self.offVals[:,2]], xlabel=self.ctrlPV_name, ylabel='onreads', formats='.')
          calib_allon = XYPlotData(self.this_t_str, 'calib_allon', [self.ctrl_vals ,self.ctrl_vals ,self.ctrl_vals ],[ self.onVals[:,0], self.onVals[:,1], self.onVals[:,2]], xlabel=self.ctrlPV_name, ylabel='onreads', formats='.')
          calib_alldiff = XYPlotData(self.this_t_str, 'calib_alldiff', [self.ctrl_vals ,self.ctrl_vals ,self.ctrl_vals ],[ self.diffVals[:,0], self.diffVals[:,1], self.diffVals[:,2]], xlabel=self.ctrlPV_name, ylabel='onreads', formats='.')
                              
          self.plotserver.send_data('calib_alloff',calib_alloff)
          self.plotserver.send_data('calib_allon',calib_allon)
          self.plotserver.send_data('calib_alldiff',calib_alldiff)

          calib_onoffM = XYPlotData(self.this_t_str, 'calib_onoffM', [self.ctrl_vals ,self.ctrl_vals ],[ self.onVals[:,1], self.offVals[:,1]], xlabel=self.ctrlPV_name, ylabel='on off reads', formats='.')
          calib_onoffR = XYPlotData(self.this_t_str, 'calib_onoffR', [self.ctrl_vals ,self.ctrl_vals ],[ self.onVals[:,2], self.offVals[:,2]], xlabel=self.ctrlPV_name, ylabel='on off reads', formats='.')
          self.plotserver.send_data('calib_onoffM',calib_onoffM)
          self.plotserver.send_data('calib_onoffR',calib_onoffR)
      
      else:
        res_arr = np.array(self.my_stepsc)

    def endrun(self, evt, env):
      if self.debug > 0:
        print '*** here in endrun'

    def definePlots(self, controlPVname='scanVar2'):
      self.plotlist=[]
      self.on_calib = XYPlotHelper(self.plotserver.send_data, 'on_calib', xlabel=controlPVname, ylabel='on', format='.')
      self.plotlist.append(self.on_calib)
      self.off_calib = XYPlotHelper(self.plotserver.send_data, 'off_calib', xlabel=controlPVname, ylabel='off', format='.')
      self.plotlist.append(self.off_calib)
      self.diff_calib = XYPlotHelper(self.plotserver.send_data, 'diff_calib', xlabel=controlPVname, ylabel='diff', format='.')
      self.plotlist.append(self.diff_calib)
      self.onM_calib = XYPlotHelper(self.plotserver.send_data, 'onM_calib', xlabel=controlPVname, ylabel='on(M)', format='.')
      self.plotlist.append(self.onM_calib)
      self.onR_calib = XYPlotHelper(self.plotserver.send_data, 'onR_calib', xlabel=controlPVname, ylabel='on(R)', format='.')
      self.plotlist.append(self.onR_calib)
      self.offM_calib = XYPlotHelper(self.plotserver.send_data, 'offM_calib', xlabel=controlPVname, ylabel='off(M)', format='.')
      self.plotlist.append(self.offM_calib)
      self.offR_calib = XYPlotHelper(self.plotserver.send_data, 'offR_calib', xlabel=controlPVname, ylabel='off(R)', format='.')
      self.plotlist.append(self.offR_calib)
      self.diffM_calib = XYPlotHelper(self.plotserver.send_data, 'diffM_calib', xlabel=controlPVname, ylabel='diff(M)', format='.')
      self.plotlist.append(self.diffM_calib)
      self.diffR_calib = XYPlotHelper(self.plotserver.send_data, 'diffR_calib', xlabel=controlPVname, ylabel='diff(R)', format='.')
      self.plotlist.append(self.diffR_calib)


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
