from psana import *
ds = DataSource('exp=xpptut15:run=59:smd')

detNames = DetNames()
print '*** Detector Names (Full-Name, DAQ-Alias, User-Alias) ***'
for detname in DetNames(): print detname

epicsNames = DetNames('epics')
print '*** Some Epics Names (Full-Name, DAQ-Alias, User-Alias) ***'
for ename in epicsNames[:4]: print ename # only print a few
