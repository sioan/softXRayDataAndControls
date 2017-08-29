import sys
import pypsepics
from pypslog import logprint
from virtualmotor import VirtualMotor
import time

class SaPiezo(VirtualMotor):
    def __init__(self, motorsobj, name, pvbase):
        self.__pvbase = pvbase
        VirtualMotor.__init__(self,
                              motorsobj,
                              name,
                              move = self.__move,
                              wm = self.__wm,
                              wait = self.__wait,
                              egu="mm"
                              )

        pass

    def __getstepsize(self):
        return pypsepics.get(self.__pvbase+":STEP_INC")

    def __wm(self):
        return pypsepics.get(self.__pvbase+":SENS_POS")/1.0e6

    def __move(self,pos):
        pypsepics.put(self.__pvbase+":GO",0)
        pypsepics.put(self.__pvbase+":STOP",1)
        pypsepics.put(self.__pvbase+":CTRL_POS",int(pos*1.0e6/self.__getstepsize()))
        pypsepics.put(self.__pvbase+":GO",1)
        pypsepics.put(self.__pvbase+":STOP",0)
        pass

    def __wait(self):
        done=False
        while not done:
            done = (pypsepics.get(self.__pvbase+":MOVE_DONE") == 1)
            if not done:
                time.sleep(.1)
            else:
                return
            pass
        pass

    #def mvr(self,delta):
    #    self.move(self.wm()+delta)

    pass
