from xppbeamline import *
# usage: mv m.filt[1],3,m.filt[3],4
def mv(*kargs):
  for i in range(len(kargs)/2):
    mot = kargs[2*i]
    pos = kargs[2*i+1]
    mot.move(pos)
    print "move",mot,"to",pos
