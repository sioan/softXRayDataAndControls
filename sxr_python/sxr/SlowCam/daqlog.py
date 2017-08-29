import time
import os
import sys

class Daqlog:
  def __init__(self):
    instrument = "sxr"
    curTime    = time.localtime(time.time()) # (2013, 10, 15, 17, 19, 26, 1, 288, 1)
    logdir     = "/reg/g/pcds/pds/" + instrument + "/logfiles/%d/%02d" % (curTime[0], curTime[1])

    curFilePath = os.path.realpath(sys.argv[0])
    curFilename = os.path.basename(curFilePath)
 
    hostname    = os.popen("hostname").read().strip()    

    # example format: 15_17:07:19_xcs-control:ami_client.log
    self.logFile = "%s/%02d_%02d:%02d:%02d_%s:%s.log" % (logdir, curTime[2], curTime[3], curTime[4], curTime[5], hostname, curFilename)
    
    self.dataLeft = ""

    self.stdout   = sys.stdout
    self.flog     = open(self.logFile, 'w')     
    sys.stdout    = self
    #print "Log file: " + self.logFile
    print "Running " + curFilePath

  def __del__(self):
    #print "closing logfile " + self.logFile 
    self.flog.flush()    
    sys.stdout = self.stdout
    self.flog.close()

  def write(self,data):
     if len(data) > 0 and data[-1] == '\r':       
       # don't write to flog
       pass
     else:
       self.flog.write(data)
     self.stdout.write(data)
    
  def flush(self):    
     #self.flog.flush() # no need to flush the logfile frequently
     self.stdout.flush()
     
log = Daqlog()
