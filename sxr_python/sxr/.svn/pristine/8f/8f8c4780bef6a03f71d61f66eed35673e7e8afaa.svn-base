import pyca
import sys
import time
from caget import caget
from Pv import Pv

DEFAULT_TIMEOUT = 60
EPICS_OVERHEAD = 2
EPICS_IO_PEND_TIME = 0.5

class EpicsField:
    def __init__(self, name, pv_base, pv_field):
        self.name=name
        self.pv_base=pv_base
        self.pv_field=pv_field
        self.value=self.get(True)
        pass

    def get_pv_name(self):
        return self.pv_base + self.pv_field

    def get(self,refresh=False):
        if refresh:
            self.value=caget(self.get_pv_name())
        return self.value

    def set(self, val, pend_io=True):
        caput(self.get_pv_name(), val)
        if pend_io:
            pyca.pend_io(EPICS_IO_PEND_TIME)
        pass    

    pass
