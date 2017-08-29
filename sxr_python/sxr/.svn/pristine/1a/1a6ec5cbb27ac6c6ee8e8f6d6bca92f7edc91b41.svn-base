#!/usr/bin/env python

import pyca 

import sys
import time


from options import Options
from donemoving import donemoving
from Pv import Pv

if __name__ == '__main__':
  options = Options(['motorpvname', 'start', 'end', 'delta'], [], [])
  try:
    options.parse()
  except Exception, msg:
    options.usage(str(msg))
    sys.exit()

  motorpvname = options.motorpvname
  position = float(options.start)
  end = float(options.end)
  delta = float(options.delta)

  try:
    motorpv = Pv(motorpvname)
    motorpv.connect(1.0)
    dmovpv = donemoving(motorpvname + '.DMOV')
    steps = int((end-position)/delta)
    for step in range(0, steps+1):
      starttime = time.time()
      motorpv.put(position)
      pyca.pend_io(.1)
      dmovpv.wait_for_done(10)
      elapsed = time.time() - starttime
      print 'pos %f time %.4f elapsed %f' %(position, starttime, elapsed)
      position += delta
  except pyca.pyexc, e:
    print 'pyca exception: %s' %(e)
  except pyca.caexc, e:
    print 'channel access exception: %s' %(e)
  except Exception, e:
    print e
