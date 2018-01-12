#!/bin/csh
#
# restart_daq.csh
#
# stop local and remote processes
#
/reg/g/pcds/dist/pds/tools/procmgr/procmgr stop \
  /reg/neh/operator/amoopr/amo.cnf 


#
# start local and remote processes
#

/reg/g/pcds/dist/pds/tools/procmgr/procmgr start \
  /reg/neh/operator/amoopr/amo.cnf -c 2000000000 -o /reg/g/pcds/pds/amo/logfiles

# /reg/g/pcds/dist/pds/tools/procmgr/procmgr status /reg/g/pcds/dist/pds/amo/scripts/amo.cnf
# /reg/g/pcds/dist/pds/tools/procmgr/procmgr stop /reg/g/pcds/dist/pds/amo/scripts/amo.cnf
# /reg/g/pcds/dist/pds/tools/procmgr/procmgr start /reg/g/pcds/dist/pds/amo/scripts/amo.cnf -c 2000000000 -o /reg/g/pcds/pds/amo/logfiles

# gather some network statistics
#
#/reg/g/pcds/dist/pds/scripts/getnetstats

#/bin/env LD_LIBRARY_PATH=/reg/g/pcds/package/python-2.5.2/lib:/reg/g/pcds/package/qt-4.3.4_x86_64/lib PATH=/reg/g/pcds/package/python-2.5.2/bin:/reg/g/pcds/package/qt-4.3.4_x86_64/bin: /reg/g/pcds/dist/pds/tools/procmgr/procstat.py -t amo -e 23 -n daq-amo-dss01+daq-amo-dss02+daq-amo-dss03   /reg/g/pcds/dist/pds/amo/scripts/p0.cnf.last
