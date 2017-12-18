from pylab import *
from pyEpics import *
import time
import random

def jamesScan(scanStart,scanEnd, numberOfSteps, dwellTime, numberOfCycles):
    caput("AMO:SAS:SHUT:01:CLS_SW","Open")
    for i in arange(numberOfCycles):
        myDelayValueArray = arange(scanStart,scanEnd,(scanEnd-scanStart)*1.0/numberOfSteps)
        random.shuffle(myDelayValueArray)
        
        for j in myDelayValueArray:
            caput("LAS:FS1:VIT:FS_TGT_TIME_DIAL",j)
            time.sleep(dwellTime)
            print j
    print("finished scanning")
