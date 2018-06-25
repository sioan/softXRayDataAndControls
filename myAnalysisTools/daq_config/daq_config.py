import psana
from pylab import *

my_list = arange(71,118)

for i in my_list:
	
	myDataSource = psana.MPIDataSource("exp=sxrlr0716:run="+str(i))
	my_events =  myDataSource.events()
	evt = next(my_events)
	env = myDataSource.env()
	configs = env.configStore()
	configs.keys()
	andor_config = configs.get(psana.Andor.ConfigV2)
	print("run = "+str(i)+ " readout speed = "+str(andor_config.readoutSpeedIndex()))



