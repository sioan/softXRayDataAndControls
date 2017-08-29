import pyca
from donemoving import donemoving
import sys
import time
from caget import caget
from math import fabs
from Pv import Pv

DEFAULT_TIMEOUT = 60
EPICS_OVERHEAD = 5

class SmartMotor:
    def __init__(self, motor_channel, motor_name=None, active_monitoring=False):
        self.motor_channel = motor_channel
        self.motor_name = motor_name
        self.active_monitoring = active_monitoring
        
        self.__move_pv = Pv(motor_channel)
        self.__move_pv.connect(1.0)
#        self.__pos_pv = Pv(self.__get_pv_name('.RBV'))
#        self.__pos_pv.connect(1.0)
        self.__dmovpv = donemoving(self.__get_pv_name('.DMOV'))

        self.update()
        pass


    def update(self):
        self.egu = self.__get('.EGU')
        self.ulim_lo = self.__get('.LLM')
        self.ulim_hi = self.__get('.HLM')
        self.base_speed = self.__get('.SBAS')
        self.speed = self.__get('.S')
        self.accel = self.__get('.ACCL')
        self.base_speed_egu = self.__get('.VELO')
        self.speed_egu = self.__get('.VELO')
        self.backlash_speed = self.__get('.SBAK')
        self.backlash_accel = self.__get('.BACC')
        self.backlash_dist = self.__get('.BDST')
        if (self.motor_name is None):
            self.motor_name = self.__get('.DESC')
            pass
        pass

    # TODO:  Add logic to consider backlash:
    def is_in_range(self, pos):
        return not (pos < self.ulim_lo or pos > self.ulim_hi)
        pass

    # TODO:  Add logic to consider backlash:
    def why_outside_range(self, pos):
        if (pos < self.ulim_lo):
            return "Position (%f%s) exceeds user low-limit (%f%s) for '%s.'" % (pos, self.egu, self.ulim_lo, self.egu, self.motor_name)
        elif (pos > self.ulim_hi):
            return "Position (%f%s) exceeds user high-limit (%f%s) for '%s.'" % (pos, self.egu, self.ulim_hi, self.egu, self.motor_name)
        else:
            return "Position (%f%s) is within user limits [%f,%f]%s for '%s.'" % (pos, self.egu, self.ulim_lo, self.ulim_hi, self.egu, self.motor_name)
        

    def is_in_range_relative(self, offset):
        return is_in_range(self.get_position() + offset)


    def get_position(self):
        return caget(self.__get_pv_name('.RBV'))
#        self.__pos_pv.get(False, 5.0)
#        return self.__pos_pv.value



    def move(self, pos):
        self.__move_pv.put(pos)
        pyca.pend_io(.5)
        pass

    def wait(self, timeout=DEFAULT_TIMEOUT):
        self.__dmovpv.wait_for_done(timeout)


    def move_wait(self, pos, timeout=None):
        if timeout==None:
            timeout = self.get_move_time(pos)
        self.move(pos)
        self.wait(timeout)
#        self.__dmovpv.wait_for_done(timeout)
        pass


    def move_relative(self, offset):
        self.move(self.get_position() + offset)
        pass


    def move_relative_wait(self, offset, timeout=None):
        pos = self.get_position() + offset
        if timeout==None:
            timeout = self.get_move_time(pos)
        self.move_wait(pos, timeout)
        pass

    def __get_pv_name(self, pv_field):
        return self.motor_channel + pv_field


    def __get(self, pv_field):
        return caget(self.__get_pv_name(pv_field))


    def __put(self, pv_field, value):
        caput(self.__get_pv_name(pv_field), value)
        pass


    def get_dist_to(self, pos):
        return fabs(pos-self.get_position())


    # TODO: Add logic to consider backlash
    def get_move_time(self, pos):
        return fabs(self.get_dist_to(pos) / self.speed_egu) + 2*self.accel + EPICS_OVERHEAD

#    def get_move_time2(self, pos):
#        return fabs(self.get_dist_to(pos) / self.speed_egu) + 2*self.accel + EPICS_OVERHEAD


    # todo: add backlash checks
    def checkLimits(self):
        lim_lo = self.__get('.LLS')
        if (lim_lo == 1):
            return -1
        else:
            lim_hi = self.__get('.HLS')
            if (lim_hi == 1):
                return 1
            else:
                return 0
            pass
        pass

    # TODO: This should pickle the important motor parameters to file
    def saveMotor(self, file, name):
        parms = {}
        parms['DESC']=self.name
        pass

    # TODO: Maybe make this a global which returns a motor instance?
    # TODO: This should load a pickled record from a file
    def loadMotor(self, file, name):
        
        pass

    # TODO: This should install the important motor parameters to a user motor channel
    def installTo(self, channel, restict=True):
        if restrict and channel.split(':')[1]!='USR':
            raise Exception("Request refused.  Destination channel is not a user motor.")
        else:
            pass        
        pass
    
    pass


