import pyca
from Pv import Pv
import threading



class donemoving(Pv):
    def __init__(self, name):
        Pv.__init__(self, name)
        self.monitor_cb = self.monitor_handler
        self.__sem = threading.Event()
        self.__moving = False
        timeout = 1.0
        self.connect(timeout)
        evtmask = pyca.DBE_VALUE | pyca.DBE_LOG | pyca.DBE_ALARM
        self.monitor(evtmask, ctrl=False)

    def wait_for_done(self, timeout):
        self.__sem.wait(timeout)
        if self.__sem.isSet():
            self.__sem.clear()
        else:
            raise Exception, 'Timedout (%d sec) while waiting for stop: %s' %\
                             (timeout, self.name)

    def monitor_handler(self, exception=None):
        try:
            if exception is None:
                if self.value == 1:
                    if self.__moving == True:
                        self.__sem.set()
                    self.__moving = False
                else:
                    self.__moving = True
            else:
                print "%-30s " % (self.name), exception
        except Exception, e:
            print e
