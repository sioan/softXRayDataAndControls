#run this in shell before executing
#source /reg/g/psdm/etc/ana_env.csh

import os
import pylab 
import psana

ds = DataSource('exp=xpptut15:run=54')

evt = ds.events.next()


