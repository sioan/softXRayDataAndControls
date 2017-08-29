import sys
import os
import time

# Mark spot settings
y_mark_start = 102
y_mark_end = 108
y_mark_attenuator = 2.0
y_mark_burst = 100

# Set y starting position, distance between imprints, and number of imprints 
# -- Units are in mm
yStart = 102.5
deltaY = -0.5
n_imprints = 10

# -- Number of FEL shots per Burst request
burstValues = (100,100,100,100,100,100,100,100,100,100)

# --- Set Attenuator values here: Units are Torr
#attenuatorValues = (3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.25, 6.5, 6.75, 7.0, \
#                    7.25, 7.5, 7.75, 8.0, 8.25, 8.5, 8.75, 
#                    9.25, 9.5, 9.75, 10.0, 10.25, 10.5, 10.75,11.0 )


attenuatorValues = (2,2,2,2,2,2,2,2,2,2)





########################################
# START OF SCRIPT    ###################
########################################

#### Mark before scan starts
print "Set beginning mark spot"

# Set Attenuator
att_EPICS=  "caput GATT:FEE1:310:P_DES " + str(y_mark_attenuator)
print "wait for attenuator to settle"
os.system(att_EPICS)
time.sleep(10)

# Set y motor
y_EPICS = "caput SXR:EXP:MMS:02 "+str(y_mark_start)
os.system(y_EPICS)

# Request burst
print "Request burst with", y_mark_burst, "FEL shots"
nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(y_mark_burst)
os.system(nFEL_shots_EPICS)
burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1" 
os.system(burst_EPICS)

print y_EPICS," ",att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
time.sleep(1.5)        




#### Start scan 
print "Starting scan"
yPos = yStart

for yStep in range(n_imprints):
 
    # Set Attenuator
    att_EPICS=  "caput GATT:FEE1:310:P_DES " + str(attenuatorValues[yStep])
    print "wait for attenuator to settle"
    os.system(att_EPICS)
    if yStep == 0:
        time.sleep(10)
    else:
        time.sleep(10)

    # Set y motor
    y_EPICS = "caput SXR:EXP:MMS:02 "+str(yPos)
    os.system(y_EPICS)
    
    # Request burst
    print "Request burst with",burstValues[yStep], "FEL shots"
    nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(burstValues[yStep])
    os.system(nFEL_shots_EPICS)
    burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"  
    os.system(burst_EPICS)
    
    print y_EPICS," ",att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
    time.sleep(1.5)        
    
    yPos = yPos + deltaY


print "Scan finished"


#### Mark before scan starts
print "Set end mark spot"

# Set Attenuator
att_EPICS=  "caput GATT:FEE1:310:P_DES " + str(y_mark_attenuator)
print "wait for attenuator to settle"
os.system(att_EPICS)
time.sleep(10)

# Set y motor
y_EPICS = "caput SXR:EXP:MMS:02 "+str(y_mark_end)
os.system(y_EPICS)

# Request burst
print "Request burst with", y_mark_burst, "FEL shots"
nFEL_shots_EPICS = "caput PATT:SYS0:1:MPSBURSTCNTMAX " + str(y_mark_burst)
os.system(nFEL_shots_EPICS)
burst_EPICS = "caput PATT:SYS0:1:MPSBURSTCTRL 1"
os.system(burst_EPICS)

print y_EPICS," ",att_EPICS," ",nFEL_shots_EPICS," ",burst_EPICS
time.sleep(1.5)        


print "DONE!"
