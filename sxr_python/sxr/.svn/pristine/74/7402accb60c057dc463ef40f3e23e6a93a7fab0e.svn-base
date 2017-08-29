import common.daq_new as Daq
import time

# Set up DAQ
print "Check the DAQ GUI is running and DAQ is configured"
raw_input("(press enter to contine)")

print "Connecting to DAQ - plese be patient"
daq = Daq.Daq(host='sxr-daq')
daq.record=True

# Scan every minute for 24 hrs
min_per_day = 60 * 24
npoints = min_per_day * 120
wait_time = 60

daq.configure(npoints)

for i in range(min_per_day) :
    print i,":",time.asctime(),
    daq.calibcycle(120) # Take data for 1 second
    time.sleep(wait_time)
    print "[Events:",daq.eventnum(),"]"


print "Experiment:",daq.experiment()
print "Run:",daq.runnumber()

daq.stop()

print "Done!"





