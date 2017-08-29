#!/usr/bin/env python

import sys
import os
from cafunctions  import caget, caput
from seqDefs      import *



class SequenceLoad:
    def __init__(self, event_codes=[], beam_delays=[], fiducial_delays=[], burst_requests=[], length=-1):
        if length == -1:
          self.length          = len(event_codes)
        else:
          self.length          = length
        self.event_codes     = event_codes
        self.beam_delays     = beam_delays
        self.fiducial_delays = fiducial_delays
        self.burst_requests  = burst_requests

    def load(self, verbose=False):
      
        if verbose:
            print_file = sys.stdout
        else:
            print_file = open(os.devnull, 'w')
    
        bPrintSet = True # Always print "set ..." in caput()    	
        print >> print_file, caput( pvSeqEvent    , self.event_codes    , verbose=bPrintSet)
        print >> print_file, caput( pvSeqBeamDelay, self.beam_delays    , verbose=bPrintSet)
        print >> print_file, caput( pvSeqFiduDelay, self.fiducial_delays, verbose=bPrintSet)
        print >> print_file, caput( pvSeqBurst    , self.burst_requests , verbose=bPrintSet)

        print >> print_file, caput( pvSeqLen      , self.length         , verbose=bPrintSet)

        print >> print_file, caput( pvSeqUpdate   , 1                   , verbose=bPrintSet)

        sSeqStatus  = caget(pvSeqStatus)
        iErrorIndex = int(caget(pvSeqErrorIndex))

        if sSeqStatus.find("Valid Sequence") != -1:
          print "Status: %s" % sSeqStatus
          return 0

        print "!! Status: %s  Error Index: %d" % (sSeqStatus, iErrorIndex)
        return 1
