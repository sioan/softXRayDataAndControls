#!/usr/bin/env python

import sys
import os
import getopt
import time
from cafunctions import caget, caput
from seqDefs     import *


class SeqControl:
  def __init__(self):
    pass

  def runOnce(self):
    caput(pvPlayMode, (0,)) # PlayMode = Once
    caput(pvPlayCtrl, (1,)) # PlayCtrl = Play
    
    while True:
      if caget(pvPlayStat).find("Stopped") != -1:
        break

      time.sleep(0.05)    

  def runN(self, n):
    caput(pvPlayMode,  (1,)) # PlayMode  = Repeat N
    caput(pvRepCount,  (n,))  # RepCount = n
    caput(pvPlayCtrl,  (1,)) # PlayCtrl  = Play

  def run(self):
    caput(pvPlayMode, (2,)) # PlayMode = forever
    caput(pvPlayCtrl, (1,)) # PlayCtrl = Play

  def stop(self):
    caput(pvPlayCtrl, (0,)) # PlayCtrl = Stop

  def stopAtSeqEnd(self):
    if caget(pvPlayStat).find("Stopped") != -1:
      return

    iPlayCountOld = caget(pvPlayCount)
    print "Waiting for current round to finish..."
    while True:
      iPlayCountNew = caget(pvPlayCount)
      if iPlayCountNew != iPlayCountOld:
        caput(pvPlayCtrl, (0,)) # PlayCtrl = Stop
      if caget(pvPlayStat).find("Stopped") != -1:
        break

      time.sleep(0.05)

    print "Done."
    return

def showUsage():
    sFnCmd = os.path.basename( sys.argv[0] )
    print( "Usage: %s [-h | --help] [-r|--run] [-o|--once] [-n|--nrun <NumRun>] [-a|--abort] [-e|--end]" % sFnCmd )
    print( "    -h | --help              Show usage information" )
    print( "    -r | --run               Run sequence continuously" )
    print( "    -o | --once              Run sequence for once" )
    print( "    -n | --nrun <NumRun>     Run sequence for <NumRun> times" )
    print( "    -a | --abort             Abort sequence" )
    print( "    -e | --end               End sequence (wait for current round to finish and stop)" )

def main():
    (llsOptions, lsRemainder) = getopt.getopt(sys.argv[1:], \
        'vhron:ae', \
        ['version', 'help', 'run', 'once', 'nrun=', 'abort', 'end'] )

    iNumShot = 1
    for (sOpt, sArg) in llsOptions:
        if sOpt in ('-v', '-h', '--version', '--help' ):
            showUsage()
            return 1
        elif sOpt in ('-r', '--run'):
            SeqControl().run()
        elif sOpt in ('-o', '--once'):
            SeqControl().runOnce()
        elif sOpt in ('-n', '--nrun'):
            SeqControl().runN(int(sArg))
        elif sOpt in ('-a', '--abort'):
            SeqControl().stop()
        elif sOpt in ('-e', '--end'):
            SeqControl().stopAtSeqEnd()

    return

if __name__ == '__main__':
    status = main()
    sys.exit(status)
