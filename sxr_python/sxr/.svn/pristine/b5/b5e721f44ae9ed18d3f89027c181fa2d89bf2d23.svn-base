import logging
import threading
import time

import pyca
from Pv import Pv


logging.getLogger(__name__)

class epics_shutter :
    """
    Wrapper to implment a device that uses analog out to open/close a
    shutter.

    This class is generic and can be applied to Uniblitz, laser safety
    shutters used for Yano beamtime.
    """

    def __init__(self,ctrl, rbv, open_val, close_val) :
        """
        ctrl: PV to command shutter to open/close
        rbv : PV to readback shutter status

        open_val : Value that opens shutter
        close_val: Value thst closes shutter
        """

        # Setup logger
        self.__logger = logging.getLogger(__name__)

        # Set up ctrl and rbv PVs
        self.__ctrl = Pv(ctrl)
        self.__rbv = Pv(rbv)

        # Set up values for shutter open/close
        self.__open_val = open_val        
        self.__close_val = close_val

        # Boolean values that define if a shutter is in or out
        self.__open = False
        self.__close = False

        # Connect to Pvs
        self.__connect()

        # Threading event to signal when shutter has changed state
        self.__state_change = threading.Event()
        
        # Timing and event threads to wait after shutter has opened/closed
        #self.__wait_done = threading.Event()
        #self.__wait_thread = threading.Timer(wait,self.__wait_done_cb)
        #self.__wait_thread.setName("Wait Thread")

        # Start monitors to live update shutter status
        # ..as soon as monitor starts, it will update self._open and
        # self._close 
        self.__start_monitors()

        # Set channel switch to on....



    def __connect(self) :
        """
        Connect to PVs
        """
        try:
            self.__ctrl.connect(1.0)
            self.__rbv.connect(1.0)
        except pyca.pyexc, e:
            self.__logger.error("Failed to connect or was already opened: %s"%e)
            raise
        except pyca.caexc, e:
            self.__logger.error("Channel Access Error: %s"%e)
            raise
            


    def disconnect(self) :
        """
        Disconnect PVs
        """
        self.__logger.info("Disconnecting PVs")
        
        try:
            self.__ctrl.disconnect()
            self.__rbv.disconnect()
        except pyca.pyexc, e:
            self.__logger.error("Failed to connect or was already opened: %s"%e)
            raise
        except pyca.caexc, e:
            self.__logger.error("Channel Access Error: %s"%e)
            raise



    def __start_monitors(self) :
        """
        Start EPICS monitors of rbv PV to continously update shutter state
        """
        self.__logger.debug("Starting monitor for %s"%self.__rbv.name)

        # Connect to monitor callbacks
        self.__rbv.monitor_cb = self.__rbv_cb

        # Start monitor
        pvevt = pyca.DBE_ALARM|pyca.DBE_LOG|pyca.DBE_VALUE
        self.__rbv.monitor(pvevt)
        pyca.flush_io()

        # Wait 1 second for monitoring to start
        time.sleep(1.0)



    def __stop_monitors(self) :
        """
        Stop EPICS monitors
        """
        self.__logger.debug("Stopping monitor for %s"%self.__rbv.name)
        self.__rbv.unsubscribe()
        
        
        
    def __rbv_cb(self) :
        """
        rbv call back
        """
        self.__logger.debug("%s updated"%self.__rbv.name)

        if self.__rbv.value <= (1.2 * self.__close_val) :
            self.__logger.debug("%s -- %0.1f -- CLOSE"%(self.__rbv.name,self.__rbv.value))
            self.__close = True
            self.__open = False
            self.__state_change.set()
            #self.__wait_done.clear()
            #self.__wait_thread.cancel()
            #self.__wait_thread.start()


        if self.__rbv.value >= (0.8 * self.__open_val) :
            self.__logger.debug("%s -- %0.1f -- OPEN"%(self.__rbv.name,self.__rbv.value))
            self.__close = False
            self.__open = True
            self.__state_change.set()
            #self.__wait_done.clear()
            #self.__wait_thread.cancel()
            #self.__wait_thread.start()
            
            
            
    #def __wait_done_cb(self) :
    #    self.__logger.info("CB Shutter wait done")
    #    self.__wait_done.set()
        
        
        
    def open(self) :
        self.__logger.info("Open shutter")

        if self.isOpen() :
            self.__logger.info("shuttter already opened")
        else : 
            self.__logger.info("Set %s to %0.1f"%(self.__ctrl.name,self.__open_val))
            self.__state_change.clear()
            self.__ctrl.put(self.__open_val)
            pyca.flush_io()


                
    def close(self) :
        self.__logger.info("Close shutter")


        if self.isClose() :
            self.__logger.info("shutter already closed")
        else:
            self.__logger.info("Set %s to %0.1f"%(self.__ctrl.name,self.__close_val))
            self.__state_change.clear()
            self.__ctrl.put(self.__close_val)
            pyca.flush_io()
        

        
    def isOpen(self) :
        self.__logger.info("Shutter Open: %s"%self.__open)
        return self.__open

        
    def isClose(self) :
        self.__logger.info("Shutter Close: %s"%self.__close)
        return self.__close


    def wait(self) :
        self.__logger.info("Waiting for state to change")
        self.__state_change.wait()
        #self.__logger.info("Waiting for laser")
        #self.__wait_done.wait()
        



if __name__ == "__main__" :
    import time
    logging.basicConfig(level=logging.DEBUG)
#    lasershutter = epics_shutter("SXR:EXP:MPD:CH:5:SetVoltage",
#                                 "SXR:EXP:MPD:CH:5:GetTerminalVoltageMeasurement",
#                                 24.0,1.0)

    lasershutter = epics_shutter("SXR:TST:CTRL:1","SXR:TST:RBV:1",24.0,1.0)
    
    #lasershutter.isOpen()
    #lasershutter.isClose()

    lasershutter.open()
    #lasershutter.isOpen()
    lasershutter.wait()
    #lasershutter.isOpen()
    time.sleep(2.0)

        
    lasershutter.close()
    #lasershutter.isOpen()
    #lasershutter.isClose()
    lasershutter.wait()
    #lasershutter.isOpen()
    #lasershutter.isClose()
    time.sleep(10.0)
        
