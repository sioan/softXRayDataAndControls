from Pv import Pv
import pyca


class Follower(object):
    def __init__(self,pvmonitor, pvfollower,follower_func):
        print "Creating Follower: Monitor(%s) Follow(%s)"%(pvmonitor,pvfollower)

        # Create pyca.capv to connect to PV
        self.__pvmonitor = Pv(pvmonitor)
        self.__pvfollower = Pv(pvfollower)
        
        print "Monitor Name:",self.__pvmonitor.name
        print "Follower Name:",self.__pvfollower.name

        # Set Monitor call-back for pvmonitor
        self.__pvmonitor.monitor_cb = self.update_follower

        # Set up function to calculate new value of pvfollower based
        # on pvmonitor
        self.__follower_func = follower_func

        
    def create_channel(self) :
        print "Connecting to PVs (please be patient)"

        try:
            self.__pvmonitor.connect(1.0)
            self.__pvfollower.connect(1.0)
        except pyca.pyexc, e:
            print "ERROR: Failed to connect:",e
            raise
        except pyca.caexc, e:
            print "ERROR, Channel Access Error:",e
            raise
       
            
    def clear_channel(self):
        print "Clearing channels"
        self.__pvmonitor.disconnect()
        self.__pvfollower.disconnect()
        
        
    def start_monitor(self):
        print "Start monitoring"
        pvevt = pyca.DBE_ALARM|pyca.DBE_LOG|pyca.DBE_VALUE
        self.__pvmonitor.monitor(pvevt)
        pyca.flush_io()

    def stop_monitor(self):
        print "Stop monitoring"
        self.__pvmonitor.unsubscribe()


    def update_follower(self,exception=None):
        print "Update follower"
        print self.__pvmonitor.name,"updated"

        # Get monitor value
        print "Getting",self.__pvmonitor.name,"latest value"
        self.__pvmonitor.get()
        
        # Calculate new value for follower
        new_value = self.__follower_func(self.__pvmonitor.value)

        # Set new value for follower
        print self.__pvfollower.name,new_value
        self.__pvfollower.put(new_value)
        pyca.flush_io()

        



if __name__ == "__main__" :
    import time
    import math

    def followfunc(pos) :
        newpos = 12.0 * math.sin(pos)
        return newpos


    try: 
        # Create instance of follower
        follower = Follower("SXR:EXP:MMS:22",
                            "SXR:EXP:MMS:23",
                            followfunc)

        # Open channels to PVs
        follower.create_channel()

        # Start monitoring
        follower.start_monitor()
    
        #        print "Wait 10s for montoring to start"
        #        time.sleep(10.0)

        print "Now have 2 minutes to run tests"        
        time.sleep(120.0)

        # now stop
        follower.stop_monitor()

        # close channel
        follower.clear_channel()
        
    except pyca.pyexc, e:
        print "ERROR: PYCA Error:",e
    except pyca.caexc, e:
        print "ERROR, Channel Access Error:",e
