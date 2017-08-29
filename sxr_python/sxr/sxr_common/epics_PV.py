"""
SXD extension of default (P)CDS Pv class. 
Adds default call backs for EPICS PUT/GET calls, so waits for call to
complete or raises a timeout error.

If a specific PV needs its own call-back for EPICS PUT/GET, then oen
can either:
- work directly from pyca library
- use PCDS Pv class
- subclass this class
"""
import threading
import logging

import pyca
from Pv import Pv as PCDS_PV


class epics_PV(PCDS_PV) :
    def __init__(self,name) :

        #PCDS_PV .__init__(self,name)
        super(epics_PV,self).__init__(name)

        # Start the logger
        self.__logger = logging.getLogger(__name__)
        self.__logger.debug("Creating epics_PV for %s"%self.name)

        # Set up call-backs and threading events for EPICS PUT/GET
        # -- EPICS GET
        self.getevt_cb = self.__get_cb
        self.__get_done = threading.Event()
        # -- EPICS PUT
        self.putevt_cb = self.__put_cb
        self.__put_done = threading.Event()

        self.connect_cb = self.__connect_cb
        self.__connect_done = threading.Event()


    def connect(self, timeout=None) :
        """
        Connect to the PV
        """        
        self.__logger.debug("%s Connecting"%self.name)
        super(epics_PV,self).create_channel()
        self.__connect_done.clear()
        self.__connect_done.wait(timeout)
        
        if not self.__connect_done.isSet() :
            self.__logger.error("%s connection timedout"%self.name)
            raise


    def __connect_cb(self, isconnected) :
        """
        Connection callback
        """
        self.__logger.debug("%s connect callback connected:%d"%(self.name,isconnected))
        if isconnected :
            self.__connect_done.set()
        else :
            self.__connect_done.clear()
        



        
    def get(self, ctrl=False, timeout=None) :
        """
        EPICS GET - waits for EPICS to return data or will timeout  
        """
        self.__logger.debug("%s EPICS GET"%self.name)

        # Get EPICS data        
        super(epics_PV,self).get(ctrl,-1.0)
        pyca.flush_io()

        # Wait for EPICS call to complete
        self.__get_done.clear()
        self.__get_done.wait(timeout)
        
        if not self.__get_done.isSet():
            self.__logger.warning("%s EPICS GET timedout after %d seconds"%(self.name,timeout))                                  
            raise
        

    def __get_cb(self,exception=None) :
        """
        EPICS GET Callback
        """
        self.__logger.debug("%s EPICS Get Callback"%self.name)
                
        # Set Threading Event
        self.__get_done.set()



    def put(self, value, timeout=None) :
        """
        EPICS PUT - Set EPICS PV and wait until complete or timeout
        """
        
        # Put EPICS data
        super(epics_PV,self).put_data(value,-1.0)
        pyca.flush_io()
        
        # Wait for EPICS call to complete
        self.__put_done.clear()
        self.__put_done.wait(timeout)

        if not self.__put_done.isSet():
            self.__logger.warning("%s EPICS PUT timedout after %d seconds"%(self.name,timeout))
            raise
        
        
    def __put_cb(self,exception=None) :
        """
        EPICS GET Callback
        """
        self.__logger.debug("%s EPICS Put Callback"%self.name)
        
        # Set Threading Event
        self.__put_done.set()


if __name__ == "__main__" :
    import time

    logging.basicConfig(level=logging.DEBUG)
    
    campv = epics_PV("SXR:EXS:CVV:01:AVG_IMAGE")
    campv.connect(1.0)
    campv.get(timeout=1.0)

    print campv.status
    print campt.

    #print campv.value
    
    
