from psana import *

ds = DataSource('exp=xpptut15:run=200:smd')
cd = Detector('ControlData')

for run in ds.runs():
    for nstep,step in enumerate(run.steps()):
        pvList = cd().pvControls()
        for pv in pvList:
            print 'Step',nstep,'name/value:',pv.name(),pv.value()
        for evt in step.events():
            pass
        if nstep>=2:
            import sys
            sys.exit()
