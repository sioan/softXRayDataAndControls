from caput import caput
import time 

for i in range(1000) :
    caput("SXR:TST:RBV:1",(i%2))
    caput("SXR:TST:RBV:2",(i%2))
    time.sleep(1.0)


    
