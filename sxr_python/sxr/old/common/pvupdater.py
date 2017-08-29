import threading
import pypsepics

class PVUpdater(threading.Thread):
    def __init__(self, wait, writepv):
        threading.Thread.__init__(self)
        self.__wait = wait
        self.__writepv = writepv
        pass
        
    def run(self):
        self.__wait()
        self.__writepv()
        pass

    pass
