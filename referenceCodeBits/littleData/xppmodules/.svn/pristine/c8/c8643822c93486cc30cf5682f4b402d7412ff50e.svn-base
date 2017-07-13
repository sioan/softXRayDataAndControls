#make saving as hdf5 an option
#example user code w/ cfg file
#write other's user code also as example file (ex_areaDet_movie, peak,...)

from psana import *

import numpy as np
import matplotlib.pyplot as plt
import h5py
import os
import sys
p = ["/reg/g/pcds/pds/pyca","/reg/common/package/python/2.7.2-rhel6/lib/python2.7/site-packages","/reg/common/package/mpi4py/mpi4py-1.3.1/install/lib/python"]
for pi in p:
    if not (pi in sys.path): sys.path.append(pi)

import subprocess
import threading
from littleData import littleDataReader
from littleData import littleData
from littleData import arrayData

from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from utilities import *
from PyCSPadImage.CalibPars import  findCalibFile
import time
import RegDB.experiment_info

class xpp_littleDat(object):
    def __init__(self):

        #online:
        self.debug = self.configBool('debug', False)
        self.ldr = littleDataReader()

        if rank == 0 and self.debug:
            print "*** In __init__ "

    # -------------------------------------------------------------------------
    def beginjob(self, evt, env):
        if rank == 0 and self.debug:
            print "*** In beginjob, lets start now"
        self.expname = getExpName(env)

    # -------------------------------------------------------------------------
    def beginrun(self, evt, env):
        self.readCnf()

        self.ld = littleData()
        self.eventNr = -1
        self.printFreq = 10
        if rank == 0 and self.debug:
            print "*** In beginrun: Run Number", evt.run()
        self.ldr.getConfig(env, self.debug)        
        self.time_ev_sum = 0.

        dName = self.dirname
        self.ldr.getLittleDataHdf5Pars(env, self.expname, dName)
        if (self.debug):
            print 'write files to directory: ',self.ldr.dirname,' and merged data to: ',self.ldr.outDir

        self.ldr.setEpicsUser(self.epicsPV)
        self.usrKeys, self.usrKeyStrings = self.ldr.getUserKeys(evt.keys(), areaname=self.areaname)

        self.thisRunDone=0
        self.mergeH5 = mergeLittleHdf5(self.expname, inDir=self.ldr.dirname, outDir=self.ldr.outDir)

    # ---------------------------------------------------------------------------------
    def event(self, evt, env):        
        self.time_ev_start = MPI.Wtime()
        self.eventNr += 1
        printMsg(self.eventNr, evt.run())

        # check if the xfel was on:
        xfel_status, laser_status = pumpprobe_status(evt, [self.xfel_off_code], [self.laser_off_code])

        #saving littleData now for this event only for future modules
        #and if requested, in the run summary littleData object
        ldat_local = littleData()
        if self.writeData:
            ldats = [self.ld, ldat_local]
        else:
            ldats = [ldat_local]
        for thisldat in ldats:
            self.ldr.extractValues(evt, env, thisldat)
            #print 'statii: ',xfel_status, laser_status
            self.ldr.addValueToKey(arrayData(['xray','laser'],[xfel_status, laser_status]),'lightStatus',thisldat)
                            
            #code for getting user data generated in earlier modules as we assume we care if we make that data...
            self.usrData =self.ldr.extractUserKeys(evt, self.usrKeys)
            if len(self.usrKeys) == len(self.usrData) and len(self.usrKeys)>0 :
                self.ldr.addValueToKey(arrayData(self.usrKeyStrings, self.usrData),'UserData',thisldat)
            elif self.eventNr<5 and  len(self.usrKeys)>0 :
                print 'len(self.usrKeys) != len(self.usrData) !'

        evt.put(ldat_local,'littleData')
        self.time_ev_stop = MPI.Wtime()
        self.time_ev_sum += self.time_ev_stop-self.time_ev_start

    def endrun(self, evt, env):
        print 'jobname: ',env.jobName()
        if (env.jobName()).find('shmem')>=0:
            dirname = '/reg/neh/operator/xppopr/experiments/%s/littleData/'%(self.expname)
        elif  self.dirname!='None':
            dirname = self.dirname+'/'
        elif (size<2):
            dirname = '/reg/d/psdm/xpp/%s/ftc/'%(self.expname)
        else:
            dirname = '/reg/d/psdm/xpp/%s/scratch/tmp_littleDat/'%(self.expname)
        if (self.debug):
            print 'write files to directory: ',dirname
        fname = 'ldat_%s_Run%i_rank%03d'%(self.expname,evt.run(),rank)
        self.writeDir = dirname
        self.fname = fname
        if self.writeData:
            if self.writeDataFree or evt.run() < 10000:
                if self.debug:
                    print 'write file: ',(dirname+fname)
                f = h5py.File(dirname+fname+".h5", "w")

                #we should really get which cnf file we have set up with...
                if self.cnffile=='None':
                    fcnf = "/reg/neh/operator/xppopr/experiments/littleData/ana-current/xppmodules/src/xpp_littleDat.cfg"
                else:
                    fcnf = self.cnffile
                addPsanaCnfInfoToHdf5(f, fcnf)
                    
                #now get user information from configstore and save:
                cfgKeys, cfgKeyStrings = self.ldr.getUserKeys(env.configStore().keys(), areaname=self.areaname)
                cfgData = self.ldr.extractUserKeys(env.configStore(), cfgKeys)
                self.ld.writeCfgOutputFile(f, cfgData, cfgKeyStrings, debug=False)
                self.ld.writeToOutputFile(f)
                                    
                f.close()

        if rank == 0 and self.debug:
            print "*** In endrun: rank 0 "
        if self.timeIt:
            print 'time in littleData event for rank: ', rank,' is ',self.time_ev_sum

        self.thisRunDone=1
        allRunsDone=0
        if (size > 1 ):
            allRunsDone = comm.reduce( self. thisRunDone)
            
        if rank==0 and evt.run()<9999:
            print 'size ',size, ' rank ',rank,' # of runs done: ',allRunsDone
            if allRunsDone == size and size >=2:
                print 'I will merge this now!'
                try:
                    if not (env.jobName()).find('shmem')>=0:
                        self.mergeH5.merge(evt.run())
                    else:
                        #run as thread to now block reading the new events....
                        mergeThread = threading.Thread(target=self.mergeH5.merge, args=(evt.run(),))
                        mergeThread.deamon = True
                        mergeThread.start()
                except:
                    print 'something went wrong in merging run#: ',evt.run()
                    

    def endjob(self, evt, env):
        if rank == 0 and self.debug:
            print "*** In endjob "
            #for test, open file and print keys.
            fRead = h5py.File(self.writeDir+self.fname+".h5", "r")
            print 'keys of file: ',self.writeDir+self.fname+".h5"
            print fRead.keys()
            print fRead['cnf'].keys()


    def readCnf(self):
        self.dirname = self.configStr('dirname', 'None')
        self.cnffile = self.configStr('cnffile', 'None')
        self.areaname = self.configStr('areaName', '')
        self.xfel_off_code = self.configInt('xfel_off_code', 162)
        self.laser_off_code = self.configInt('laser_off_code', 91)
        #self.evrCodes = self.configListInt('evrCodes')
        self.fileType =  self.configListStr('fileType')
        self.writeData = self.configBool('writeData', False)
        self.writeDataFree = self.configBool('writeDataFree', False)
        if self.fileType[0] == 'None':
            self.writeData = False
        if self.fileType[0] == 'Free':
            self.writeDataFree = True
        self.timeIt = self.configBool('timeIt', True)
        self.debug = self.configBool('debug', False)

        self.epicsPV = self.configListStr('epicsPV')
        
        
