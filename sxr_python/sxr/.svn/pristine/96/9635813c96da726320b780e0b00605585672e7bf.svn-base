import random

class epics_gasdet :

    def __init__(self,gasdetpv) :

        self.__basepv = gasdetpv

        self.__dropped_shot = 0
        self.__threshold = 0.0



    def connect(self) :

        print "Gas-detector",self.__basepv,"connected"


    def disconnect(self) :

        print "Gas-detector",self.__basepv,"disconnected"



    def energy(self) :
        return random.randint(1,100)

    
    def start_dropshot_counting(self, threshold=0.0) :

        self.__threshold = threshold

        print "Counting dropshot [thereshold=",self.__threshold,"]"

        # Reset internal dropped shot counter and start monitoring
        self.__dropped_shot = 0

        
    def stop_dropshot_counting(self):
        """
        Stop counting drop shots
        """
        self.__dropped_shot = 0 if random.randint(1,100) > self.__threshold  else 1
        
        

        
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

    gasdet.start_dropshot_counting(threshold=5.0)
    time.sleep(1)
    gasdet.stop_dropshot_counting()

    print "Dropped shots:",gasdet.dropped_shots()


    gasdet.disconnect()
