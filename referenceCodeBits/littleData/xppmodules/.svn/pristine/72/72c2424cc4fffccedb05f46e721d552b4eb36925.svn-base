import sys
import os

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

import time as mytime
import numpy as np
import threading
#import psutil
from psana import *
import ConfigParser
from utilities import *
import RegDB.experiment_info
from xtcav.ShotToShotCharacterization import *

class xpp_xtcav(object):
    def __init__(self):

        self.read_conf()
        self.printFreq = 1000

        if self.debug:
          print '*** here in new init'

        self.time_init = mytime.time()
        self.counter = 0

        self.xtcav_camera = psana.Source('DetInfo(XrayTransportDiagnostic.0:Opal1000.0)')
        self.XTCAVRetrieval=ShotToShotCharacterization()

    def read_conf(self, env=None):
        print 'we are reading the xtcav_conf cnf file!'
        #self.areaName = self.configStr('areaName','area')
        #self.areaSrc = self.configListStr('areaSrc')
        #self.areaROI = self.configListInt('areaROI')
        
        self.debug  = self.configBool('debug',False)
        
        self.expname = 'None'
        if env is not None:
            if (env.jobName()).find('shmem')>=0:
                self.expname = RegDB.experiment_info.active_experiment('XPP')[1]
            else:
                self.expname=env.experiment()
            self.XTCAVRetrieval.SetDataSource(env)
        
    def beginjob(self, evt, env):
        self.time_begin = mytime.time()
        print 'time init :%.2f'%(self.time_begin - self.time_init)
        if self.debug:
            print '*** here in beginjob'

        self.time_begin_done = mytime.time()
        if self.debug:
            print 'time begin :%.2f'%(self.time_begin_done - self.time_begin)
        self.time_int = 0
      
    def beginrun(self, evt, env):
        self.time_begin_run = mytime.time()
        print 'time begin-beginrun :%.2f'%(self.time_begin_run - self.time_begin)
        self.ncalib=0
        self.read_conf(env)
        if self.debug:
            print 'found run number',evt.run()
        self.nXTCAVevts = 0
        self.nSKIPevts = 0

    def event(self, evt, env):
        if self.counter < 100:
            self.printFreq = 10
        elif self.counter < 1000:
            self.printFreq = 100
        elif self.counter < 10000:
            self.printFreq = 1000
        else:
            self.printFreq = 10000
        if self.counter%self.printFreq==0:
            print 'event ',self.counter
        self.counter+=1
            
        #if self.counter<100:
        #    return;

        #if self.nXTCAVevts>=10:
        #    self.stop();
        #    return;
        
        start_time_int = mytime.time()

        if not self.XTCAVRetrieval.SetCurrentEvent(evt):
            return
      
        time,power,ok=self.XTCAVRetrieval.XRayPower()
        agreement,ok=self.XTCAVRetrieval.ReconstructionAgreement()
        results,ok=self.XTCAVRetrieval.GetFullResults()
        if not ok:
            return
        
        evt.put(power,self.xtcav_camera,'XTCAV_power')
        evt.put(agreement,self.xtcav_camera,'XTCAV_agreement')
        for key in results.keys():
            if isinstance(results[key], float) or isinstance(results[key], int):
                if self.nXTCAVevts<2:
                    print key,np.array(results[key]).shape,np.array(results[key])
                evt.put(np.array(results[key]),self.xtcav_camera,'XTCAV_'+key)
            else:
                evt.put((results[key].squeeze()),self.xtcav_camera,'XTCAV_'+key)
                if self.nXTCAVevts<2:
                    print key,results[key].squeeze().shape,results[key].squeeze()
        self.nXTCAVevts += 1

        #print 'powerECOM debugging...'
        #print results['powerECOM'].squeeze()
        #print results['powerECOM'].squeeze().shape
        ##for key in evt.keys():
        ##    print key
        #print evt.get(psana.ndarray_float64_1,psana.Source('xtcav'),'XTCAV_powerECOM')
        #print evt.get(psana.ndarray_float64_1,psana.Source('xtcav'),'XTCAV_powerECOM').shape
          
        self.time_int += (mytime.time() - start_time_int)

            
    def endrun(self, evt, env):
        if self.debug:
            print '*** here in endrun'

    def endjob(self, evt, env):
        self.time_end = mytime.time()
        if self.debug:
            print '*** here in endjob'

        print 'time for xtcav: %.2f '%(self.time_int)
        print 'time to end : %.2f'%(self.time_end - self.time_begin_done)
