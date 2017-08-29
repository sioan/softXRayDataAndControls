from sxrbeamline import lcls_linac, sxrdaqconfig, sxrevent, sxrdaq
from time import time

def burst(nshots):
  nshots = int(nshots)
  lcls_linac.set_fburst("Full")
  rate = lcls_linac.get_xraybeamrate()

  if not lcls_linac.isburstenabled():
      print "ERROR: Burst mode not enabled.  Call MCC and enable it."
      return
  
  if rate == 0:
      print "!!! beam rate is 0. Cannot setup burst. !!!"
      return
    

  print "setting burst to %d shots" % nshots

  lcls_linac.set_nburst(nshots)

#  db = sxrdaqconfig.db.get_key("BEAM")

  print "taking shots"
  try:
      sxrdaq.connect()

      eventStart = sxrdaq.eventnum()
      print "start event: %d" % eventStart

      lcls_linac.get_burst()

      print "waiting for shots..."
      while True:
          if sxrdaq.eventnum() >= eventStart + nshots:
              print "Received %d shots!" % nshots
              break
          time.sleep(0.1)
          pass


  finally:
      print "stop daq"
      sxrdaq.stop()
  
  
  
