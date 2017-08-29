import logging
import datetime

class epics_ims_motor :

    def __init__(self, motorpv) :

        self.__logger = logging.getLogger(__name__)

        self.__basepv = motorpv
        self.__logger.debug("%s Creating motor"%self.__basepv)

        self.__rbv = 0.0
        self.__dmov = 1
        self.__val = 0.0

        

    def mv(self,position) :

        self.__logger.info("%s Move motor to %0.6f"%(self.__basepv,position))

        self.__val = position
        self.__dmov = 0


    def mvr(self,nudge) :

         self.__logger.info("%s Nudge motor by %0.6f"%(self.__basepv,nudge))

         self.mv(self.rbv() + nudge)


    def rbv(self) :
        return self.__rbv


    def wait_for_motion(self) :

        self.__logger.info("%s Waiting for motion to complete"%self.__basepv)        
        time_start = datetime.datetime.now()


        # wait for some time and update values
        self.__rbv = self.__val
        self.__dmov = 1


        time_end = datetime.datetime.now()
        time_diff = time_end -time_start
        self.__logger.debug("%s Motion complete (time taken:%0.2f)"%(self.__basepv,time_diff.total_seconds()))




        
    


if __name__ == "__main__" : 
#    logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
    
    motor21 = epics_ims_motor("SXR:EXP:MMS:31")

    print "Create Motor"
    motor22 = epics_ims_motor("SXR:EXP:MMS:32")
    print "Motor created"

    motor22.mv(10.0)
    motor22.wait_for_motion()

    motor22.mvr(-20.0)
    motor22.wait_for_motion()
    motor22.wait_for_motion()
