import pyca
from Pv import Pv
from caget import caget

class epics_gasdet :
    """
    Wrapper for FEE gas detector.
    Provides convenience methods to grab FEE gas detector PVs, and
    monitor for dropped shots
    """
        
    def __init__(self,gasdetpv) :
        """
        gasdetpv: Base EPCIS PV for FEE gas detector        
        """

        # Set up gas detector PV
        self.__basepv = gasdetpv

        # Connect to gas detector PVs
        self.__energy_pv = Pv(self.__basepv + ":ENRC")
        
        # Internal dropped shot counter
        self.__dropped_shot = 0

        # Internal threshold to define dropped shots
        self.__threshold = 0.0
        
        
    def connect(self,timeout=1.0) :
        """
        connect to gas detector
        timeout: time to wait for EPICS connectrion (option)
        """
        try:
            self.__energy_pv.connect(timeout)
            print "Gas-detector",self.__basepv,"connected"
        except pyca.pyexc, e:
            print "ERROR: Failed to connect or was already opened:",e
            raise
        except pyca.caexc, e:
            print "ERROR: Channel Access Error:",e
            raise
        
        
    def disconnect(self) :
        """
        Disconnect from gas detector
        """
        try:
            self.__energy_pv.disconnect()
        except pyca.pyexc, e:
            print "ERROR: Failed to disconnect or was not opened:",e
            raise
        except pyca.caexc, e:
            print "ERROR: Channel Access Error:",e
            raise
        

    def energy(self,timeout=1.0):
        """
        Get gas detector energy (mJ)
        """
        try:
            self.__energy_pv.get(timeout=timeout)
            pyca.flush_io()
            return self.__energy_pv.value
        except pyca.pyexc, e:
            print "ERROR: Failed to get gas-detector energy:",e
            raise
        except pyca.caexc, e:
            print "Error: Channel Access Error:",e
            raise
        
        
    def start_dropshot_counting(self,threshold=0.0):
        """
        Monitor gasdet energy value and count number of dropped shots,
        defined as number of below threshold readings 
        """        
        # Set threshold
        self.__threshold = threshold

        # Set up monitor call back for gas-detector energy reading
        self.__energy_pv.monitor_cb = self.__energy_cb

        print "Counting dropshot [thereshold=",self.__threshold,"]"

        # Reset internal dropped shot counter and start monitoring
        self.__dropped_shot = 0
        
        pvevt = pyca.DBE_ALARM|pyca.DBE_LOG|pyca.DBE_VALUE
        self.__energy_pv.monitor(pvevt)
        pyca.flush_io()
        
        
    def __energy_cb(self,exception=None):
        """
        Private callback to monitor gas-detector energy and count
        dropped shots
        """        
        # Get the data
        self.__energy_pv.get()

        # Increment dropped shot counter if below threshold
        if (self.__energy_pv.value < self.__threshold) :
            #print self.__basepv,self.__energy_pv.value,"mJ",
            #print "==> DROPPED SHOT"
            self.__dropped_shot += 1


            
            
    def stop_dropshot_counting(self) :
        """
        Stop counting drop shots
        """
        self.__energy_pv.unsubscribe()   
        
        
    def dropped_shots(self) :
        """
        Return the number of dropped shots 
        """
        return self.__dropped_shot
        
    


if __name__ == "__main__" :

    import time
    gasdet = epics_gasdet("GDET:FEE1:241")
    gasdet.connect()


    print "Energy (mJ):",gasdet.energy()
    
    print "Count dropped shots with threshold at 0.5"

    gasdet.start_dropshot_counting(threshold=0.0)
    time.sleep(10)
    gasdet.stop_dropshot_counting()

    print "Dropped shots:",gasdet.dropped_shots()


    gasdet.disconnect()
