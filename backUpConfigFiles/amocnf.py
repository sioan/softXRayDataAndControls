# paths for binaries

#
#  reference amo/devel
#
base_path = '/reg/g/pcds/dist/pds/amo/current/build'
ami_base_path = '/reg/g/pcds/dist/pds/amo/ami-current/build'
pdsapp_path         = base_path+'/pdsapp/bin/i386-linux-opt'
pdsappdbg_path      = base_path+'/pdsapp/bin/i386-linux-dbg'
pdsapp64_path       = base_path+'/pdsapp/bin/x86_64-linux-opt'
pdsapp64dbg_path    = base_path+'/pdsapp/bin/x86_64-linux-dbg'
pdsappRH7_path      = base_path+'/pdsapp/bin/x86_64-rhel7-opt'
pdsappRH7dbg_path   = base_path+'/pdsapp/bin/x86_64-rhel7-dbg'
pdsdata_path    = '/reg/common/package/pdsdata/8.6.8/x86_64-linux-dbg/bin'
ami_path        = ami_base_path+'/ami/bin/x86_64-linux-dbg'
amiRH7_path     = ami_base_path+'/ami/bin/x86_64-rhel7-opt'
plugin_path     = ami_base_path+'/ami/lib/x86_64-rhel7-opt'
daq2epics_path  = base_path+'/../tools/scripts'
timetool_path   = base_path+'/timetool/lib/x86_64-linux-opt/libttappmtdb.so'
#pdsappv_path = '/usr/bin/valgrind --log-file=/tmp/val.log --leak-check=full '+pdsapp64_path

old_monshm_path = '/reg/g/pcds/dist/pds/8.0.1-p8.1.7/build/pdsapp/bin/x86_64-linux-opt'
#old_monshm_path = pdsapp64_path

andor_path = pdsapp64_path
pimax_path = base_path+'/pdsapp/bin/x86_64-rhel6-dbg'

configdb_path=   '/reg/g/pcds/dist/pds/amo/misc/.configdbrc'
offlinerc_path = '/reg/g/pcds/dist/pds/amo/misc'
onlinextc_path = '/u2/pcds/pds/amo'
ami_style = '-stylesheet=/reg/g/pcds/dist/pds/amo/misc/ami_style.txt'

instrument = 'AMO'
expname    = 'expname'
expnum     = 'expnum'
currentexpcmd = pdsapp64_path+'/currentexp'
#camera_opt  = ' -C 0'
camera_opt  = ''

max_evt_sz = '0x1400000'
ami_group_base  = '239.255.34'
#ami_threads = 1
ami_threads = 6
ami_opts = '-R -L '+plugin_path+'/libtimetooldbd.so'
#ami_opts = '-L '+plugin_path+'/libtimetooldbd.so'
#ami_opts = '-R'
#ami_opts = ' '
#ami_opts = ami_opts+' -X /reg/g/pcds/pds/amo/ami/current'


# NB: slow_readout MUST be set for SLOW cameras
#slow_readout = '1' # for princeton and andor
slow_readout = '0' # for non-princeton

# NB: set the monitoring node configuration mode
# 0: Default Mode - balanced AMI/PSANA setup
# 1: SPI Mode - more PSANA, less AMI
# 2: All AMI mode - all monitoring nodes used by ami - good for 'SLOW' cameras (sz: pre config not yet implemented in AMO)
# 3: ()Single psana node mode - one monitoring node for psana the rest for AMI (sz: pre config not yet implemented in AMO)
mon_node_mode = 0


# default platform number, represented as a string
if not platform: platform = '0'
#
# FEZ addresses:
amo_daq          = '172.21.20.40'
daq_amo_mon01    = '172.21.20.141'
daq_amo_mon02    = '172.21.20.142'
daq_amo_mon03    = '172.21.20.143'
daq_amo_mon04    = '172.21.20.121'
daq_amo_mon05	 = '172.21.20.48'
daq_amo_mon06	 = '172.21.20.75'

daq_amo_dss01    = '172.21.20.21'
daq_amo_dss02    = '172.21.20.26'
daq_amo_dss03    = '172.21.20.79'
daq_amo_dss04    = '172.21.20.82' 
daq_amo_dss05    = '172.21.20.90'
daq_amo_dss06    = '172.21.20.103'
daq_amo_evr01    = '172.21.20.158'
daq_amo_master   = '172.21.20.34' #Master timing crate


# Generic Acqiris Crate Names
daq_amo_acq01     = '172.21.20.37' # (old ITOF)
daq_amo_acq02     = '172.21.20.36' # (old GDET)
daq_amo_acq03     = '172.21.20.38' # (old MBES)
daq_amo_acq04     = '172.21.20.35' # (old ETOF)

daq_amo_cam01  = '172.21.20.76'
daq_amo_cam02  = '172.21.20.92'
daq_amo_usr1   = '172.21.20.83'
daq_det_pnccd01  = '172.21.23.34'
daq_det_pnccd02  = '172.21.23.27'
psanaamo         = '172.21.20.115'
daq_amo_ana02    = '172.21.20.94'
rce08            = '172.21.20.109'
rce09            = '172.21.20.110'
rce68            = '172.21.20.112'
rce69            = '172.21.20.111'
daq_sxd_spec     = '172.21.23.33'


# Default setup
# - always have all DSS nodes included
dss_nodes = [ daq_amo_dss01, daq_amo_dss02, daq_amo_dss03, daq_amo_dss04, daq_amo_dss05, daq_amo_dss06 ]

# Default AMI/PSANA MON node setup
# - AMI MON Nodes:   MON01,MON02,MON03
# - PSANA MON Nodes: MON04,MON05,MON06
if mon_node_mode == 0:
   mon_nodes = [ daq_amo_mon01, daq_amo_mon02, daq_amo_mon03 ]
   psana_mon_nodes = [ daq_amo_mon04, daq_amo_mon05, daq_amo_mon06 ]
#
# SPI Mode (or other PSANA heavy experiments)
# - AMI MON Nodes:    MON01
# - PSANA MON Nodes:  MON02,MON03,MON04,MON05,MON06
elif mon_node_mode == 1:
   mon_nodes = [ daq_amo_mon01]
   psana_mon_nodes = [ daq_amo_mon02, daq_amo_mon03, daq_amo_mon04, daq_amo_mon05, daq_amo_mon06 ]

#proxy_node = daq_amo_dss06
proxy_node = daq_amo_dss05
# dead nodes -dd
#proxy_node = daq_amo_dss04
proxy_cds = proxy_node.replace('.20.','.37.')

# AMO trigger cabling: (7/16/10)
# evrB: (counting from zero)
# 0. MBES 1. ITOF 2. GASDET 3. ETOF 4. VMI 5. BPS1 6. BPS2
#
# -i argument enumeration
# enum Detector {NoDetector,AmoIms,AmoGasdet,AmoETof,AmoITof,AmoMbes,AmoVmi,AmoBps,
#                Camp,NumDetector};
#
# procmgr FLAGS: <port number> static port number to keep executable
#                              running across multiple start/stop commands.
#                "X" open xterm
#                "s" send signal to child when stopping
#
# HOST       UNIQUEID      FLAGS  COMMAND+ARGS
# list of processes to run
#   required fields: id, cmd
#   optional fields: host, port, flags

procmgr_config_base = [
#  { host:daq_amo_dss01, id:'source',        port:'29150',  cmd:pdsappRH7_path+'/source '+daq_amo_dss01},
  { host:daq_amo_dss02, id:'source',        port:'29150',  cmd:pdsappRH7_path+'/source '+daq_amo_dss02},
#  { host:amo_daq,       id:'daq2epics',     port:'29151',  cmd:daq2epics_path+'/daq2epics.sh -P AMO'},
 { host:amo_daq,       id:'daq2epics',     port:'29151',  cmd:daq2epics_path+'/daq2epics.sh    AMO'},
  {                                       id:'control_gui',  flags:'sp',         cmd:pdsapp64_path+'/control_gui -D '+configdb_path+' -P AMO -X amo-daq:29990 -C '+offlinerc_path+'/.iocrc -L '+offlinerc_path+'/.offlinerc'},
  # Rack16 Triggers
   {host:daq_amo_master,  id:'evr0',        flags:'sp', rtprio:'50', cmd:pdsapp_path+'/evr -r b -i "0/0/0" -E 40-46,67-82,140-146'},
   {host:daq_amo_evr01,   id:'evr1',        flags:'sp',              cmd:pdsappRH7_path+'/evr -r a -i "0/0/1" -E 40-46,67-82,140-146'},
   {host:daq_amo_master,  id:'evrp',        cmd:pdsapp_path+'/evrstandalone -r a -p 40,23800,11900,0 -p 40,23800,11900,1 -k'}, # pnCCD clear signal 120Hz 

  # Detectors 
# ------ Acq temperature readout option: -T <PV> ---------------------
  {host:daq_amo_acq01,       id:'ACQ1',   flags:'sup', evr:'0,0', rtprio:'50',  
   env:'PATH=/reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86', cmd:pdsapp_path+'/acq -P AMO:DAQ:ACQ1 -i 23 -d 1'}, # OLD ITOF 
  {host:daq_amo_acq02,       id:'ACQ2',   flags:'sup', evr:'0,1', rtprio:'50',
   env:'PATH=/reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86', cmd:pdsapp_path+'/acq -P AMO:DAQ:ACQ2 -i 23 -d 2'}, # OLD GD
  {host:daq_amo_acq03,       id:'ACQ3',  flags:'sup', evr:'0,2', rtprio:'50',
   env:'PATH=/reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86', cmd:pdsapp_path+'/acq -P AMO:DAQ:ACQ3 -i 23 -d 3'}, # OLD MBES
  {host:daq_amo_acq04,       id:'ACQ4',   flags:'sup', evr:'0,3', rtprio:'50',
   env:'PATH=/reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86', cmd:pdsapp_path+'/acq -P AMO:DAQ:ACQ4 -i 23 -d 4'}, # OLD ETOF


# AMO OPAL Cameras
#  -c 0 ==> Left EDT port  |     -c 1 ==> Right EDT port

  {host:daq_amo_cam01,      id:'OPAL1',   flags:'sup', evr:'0,4',  cmd:pdsappRH7_path+'/camedt -i "AmoEndstation/0/Opal1000/1" -g 0 -c 0 '+camera_opt+ ' -L '+timetool_path}, # Left
  {host:daq_amo_cam01,      id:'OPAL2',   flags:'sup', evr:'0,5',  cmd:pdsappRH7_path+'/camedt -i "AmoEndstation/0/Opal1000/2" -g 0 -c 1 '+camera_opt+ ' -L '+timetool_path}, # Right

  {host:daq_amo_cam02,      id:'OPAL3',   flags:'sup', evr:'0,6',  cmd:pdsappRH7_path+'/camedt -i "AmoEndstation/0/Opal1000/3" -g 0 -c 0 '}, # Left
  {host:daq_amo_cam02,      id:'OPAL4',   flags:'sup', evr:'0,7',  cmd:pdsappRH7_path+'/camedt -i "AmoEndstation/0/Opal1000/4" -g 0 -c 1 '+camera_opt+ ' -L '+timetool_path}, # Right


# BLD and EPICS-ARCH machines
  {host:daq_amo_dss04,      id:'bldeb',    flags:'sp',           cmd:pdsappRH7_path+'/bld -m 0xa000000004000007'},
  {host:daq_amo_dss04,      id:'epicsArch',flags:'sp', env:'PATH=/reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86_64/', cmd:pdsappRH7_path+'/epicsArch -f  '+offlinerc_path+'/epicsArch.txt'},

   # PnCCD racks
   {host:daq_det_pnccd01,    id:'pnccdFront',     flags:'sup', evr:'0,8', cmd:pdsapp64_path+'/pnccd -P 0xf0 -d Camp -i 0 -D 0x20 -t PNCCD:FRONT:SELFTRIGGER -f /reg/g/pcds/dist/pds/amo/misc/pnccdconfig/camp1/pnccdParam2Daq'},
#   {host:daq_det_pnccd01,    id:'pnccdFront',     flags:'sup', evr:'0,8', cmd:pdsapp64_path+'/pnccd -P 0xf0 -d Camp -i 0 -D 0x20 -f /reg/g/pcds/dist/pds/amo/misc/pnccdconfig/camp1/pnccdParam2Daq'},
   {host:daq_det_pnccd02,    id:'pnccdBack',      flags:'sup', evr:'0,9', cmd:pdsapp64_path+'/pnccd -P 0xf0 -d Camp -i 1 -D 0x20 -t PNCCD:BACK:SELFTRIGGER -f /reg/g/pcds/dist/pds/amo/misc/pnccdconfig/camp2/pnccdParam2Daq'},

   # Princeton cameras
  #{host:daq_amo_cam01,    id:'princeton0',  flags:'spX',          cmd:pdsapp_path+'/princeton -n -c 0 -l 5 -i "23/0/0" '+camera_opt},
  #{host:daq_amo_cam02,    id:'princeton1',  flags:'spX',          cmd:pdsapp_path+'/princeton -n -c 0 -l 5 -i "23/0/1" '+camera_opt},

  # Andor cameras
#  {host:daq_amo_cam01, id:'andor',     flags:'spx',    evr:'0,7',    cmd:andor_path+'/andor -t AMO:ANDOR0:TEMP -n -d -c 0 -l 5 -i "23/0/0" -g ' + configdb_path},

  # Pimax cameras
#  {host:daq_amo_cam03, id:'pimax',     flags:'spux',        cmd:pimax_path+'/pimax -n -c 0 -l 5 -i "23/0/0" -g ' + configdb_path, 'env':'PUREGEV_ROOT=/reg/g/pcds/package/external/picam-2.6.1/pleora/ebus_sdk GENICAM_ROOT=/reg/g/pcds/package/external/picam-2.6.1/pleora/ebus_sdk/lib/genicam GENICAM_ROOT_V2_2=/reg/g/pcds/package/external/picam-2.6.1/pleora/ebus_sdk/lib/genicam GENICAM_LOG_CONFIG=/reg/g/pcds/package/external/picam-2.6.1/pleora/ebus_sdk/lib/genicam/log/config/DefaultLogging.properties GENICAM_LOG_CONFIG_V2_2=/reg/g/pcds/package/external/picam-2.6.1/pleora/ebus_sdk/lib/genicam/log/config/DefaultLogging.properties GENICAM_CACHE=/tmp GENICAM_CACHE_V2_2=/tmp'},
  #{host:daq_amo_cam03, id:'pimax',     flags:'spx',        cmd:pimax_path+'/pimax -n -c 0 -l 5 -i "23/0/0" -g ' + configdb_path},

  # USB encoder
  #{host:daq_amo_cam01,    id:'usdusb',  flags:'sp', evr:'0,5', cmd:pdsappRH7_path+'/usdusb -i 23'},

  # Ocean Optics spectrometer
#   {host:daq_amo_usr1,      id:'oospec_0',     flags:'sp',    cmd:pdsappRH7_path+'/oceanoptics -i "23/0/0" -d 0 -l 2'},

## Portable Spectrometer ANDOR Mar 2016
## NB: DON'T FORGET TO SET slow_readout AT TOP OF CNF FILE IF NOT RUNNING IN FULL VERTICAL BINNING MODE !
#  {host:daq_sxd_spec, id:'andor', flags:'sxpu', evr:'1,0', cmd:andor_path+'/andor -t SXD:ANDOR0:TEMP -n -d -c 0 -l 5 -i "23/0/0" -g ' + configdb_path},


  # Offline observation
  {                                       id:'offlineobs',       flags:'sp',      cmd:pdsapp64_path+'/offlineobs -P AMO -L '+offlinerc_path+'/.offlinerc -V /reg/g/pcds/dist/pds/amo/misc/logbook.txt'},

  # procstat
  {                     id:'procstat',   flags:'s',     env:'LD_LIBRARY_PATH=/reg/g/pcds/package/python-2.5.2/lib:/reg/g/pcds/package/qt-4.3.4_x86_64/lib PATH=/reg/g/pcds/package/python-2.5.2/bin:/reg/g/pcds/package/qt-4.3.4_x86_64/bin: PYTHONPATH=', cmd:'/reg/g/pcds/dist/pds/tools/procmgr/procstat.py -t amo -e '+expnum+' -n '+'+'.join(dss_nodes)+' -p '+platform+'  /reg/g/pcds/dist/pds/amo/scripts/p'+platform+'.cnf.last'},

  {                     id:'vmon',       flags:'sp',    cmd:pdsapp64dbg_path+'/vmonrecorder -P AMO -o /reg/g/pcds/pds/amo/vmon/current'},
  ]

#
#  'event' processes are handled here
#
procmgr_config_dss = []
for i in range(len(dss_nodes)):
   slice = '%d'%i
#   procmgr_config_dss.append({host:dss_nodes[i], id:'event'+slice, flags:'sp', cmd:pdsappRH7_path+'/event -d -s '+slice+' -f '+onlinextc_path+' -b '+max_evt_sz+' -c 0x47ccccccc'})
   procmgr_config_dss.append({host:dss_nodes[i], id:'event'+slice, flags:'sp', cmd:pdsappRH7_path+'/event -d -s '+slice+' -f '+onlinextc_path+' -b '+max_evt_sz+' -r -c 0x1700000000 -n 64 -w ' + slow_readout })

#0x1700000000
#  monitoring processes are handled here
#
ami_group_top = ami_group_base+'.0'
procmgr_config_mon = []
for i in range(len(mon_nodes)):
	slice = '%d'%i
	mask = '%d'%(1<<i)
	ami_group = ami_group_base+'.%d'%(i+1)

	procmgr_config_mon.append({host:mon_nodes[i], id:'monreqsrvami'+slice, flags:'sp',    cmd:pdsappRH7_path+'/monreqserver -c -P '+instrument+' -i '+mask+' -n 16 -s '+max_evt_sz+' -d -q %d'%ami_threads}),
	procmgr_config_mon.append({host:mon_nodes[i], id:'amicoll'+slice, flags:'s', cmd:amiRH7_path+'/ami_collection -I '+mon_nodes[i]+' -S '+ami_group_top+' -i lo -s '+ami_group})

	for j in range(ami_threads):
		mslice = '%d'%(j+0)
		procmgr_config_mon.append({host:mon_nodes[i], id:'ami'+slice+'-'+mslice, flags:'s', cmd:amiRH7_path+'/ami -p '+instrument+' -i lo -s '+ami_group+' -n '+mslice+' '+ami_opts})

   #
   # CAMP-specific example
   #

procmgr_config_mon.append({host:proxy_node, id:'ami_proxy', flags:'s', cmd:amiRH7_path+'/ami_proxy -I '+proxy_cds+' -i '+proxy_node+' -s '+ami_group_top})

procmgr_config_mon.append({id:'ami_client', flags:'s', cmd:ami_path+'/online_ami -I eth0 -i eth0 -s '+proxy_cds+' -f /reg/neh/operator/amoopr/'+expname})
#procmgr_config_mon.append({id:'ami_client', flags:'s', cmd:ami_path+'/online_ami -I eth0 -i eth0 -s '+proxy_cds+' -f /reg/neh/operator/amoopr/'+expname+' -n '+','.join(mon_nodes)})




############################################################
#
### PSANA SHMEM SERVERS ####
# DSS-NODE    DSS01  DSS02  DSS03  DSS04  DSS05  DSS06
# MASK BIT      1      2      4      8     16     32
#
############################################################


############################################################
#This is for 3 psana and 3 AMI 
# ****  Default mapping, 2 DSS nodes per PSANA node ****
# [ staggered for crude load balancing attempt ]
#  daq-amo-mon04 => subscribe to DSS01 and DSS04
#   => mask = 1 + 8 = 9

if mon_node_mode == 0:
   procmgr_config_mon.append({host:daq_amo_mon04,  id:'monreqsrv_psana_0', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 9 -n 32 -s '+max_evt_sz })

   # daq-amo-mon05 => subscribe to DSS02 and DSS05
   #  => mask = 2 + 16 = 18
   procmgr_config_mon.append({host:daq_amo_mon05,  id:'monreqsrv_psana_1', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 18 -n 32 -s '+max_evt_sz })

   # daq-amo-mon06 => subscribe to DSS03 and DSS06
   #  => mask = 4 + 32 = 36
   procmgr_config_mon.append({host:daq_amo_mon06,  id:'monreqsrv_psana_2', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 36 -n 32 -s '+max_evt_sz })
############################################################



#JBT############################################################
#JBT#
#JBT# ****  SPI mapping, ~1 DSS nodes per PSANA node ****
#JBT# [ staggered for crude load balancing attempt ]
#JBT#
elif mon_node_mode == 1:
   #JBT# daq-amo-mon02 => subscribed to DSS01 
   #JBT#   => mask = 1 
   procmgr_config_mon.append({host:daq_amo_mon02,  id:'monreqsrv_psana_0', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 1 -n 32 -s '+max_evt_sz })
   #JBT
   #JBT# daq-amo-mon03 => subscribed to DSS02
   #JBT#   => mask = 2
   procmgr_config_mon.append({host:daq_amo_mon03,  id:'monreqsrv_psana_1', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 2 -n 32 -s '+max_evt_sz })
   #JBT
   #JBT# daq-amo-mon04 => subscribed to DSS04
   #JBT#   => mask = 8
   procmgr_config_mon.append({host:daq_amo_mon04,  id:'monreqsrv_psana_2', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 8 -n 32 -s '+max_evt_sz })
   #JBT
   #JBT# daq-amo-mon05 => subscribed to DSS05
   #JBT#   => mask = 16
   procmgr_config_mon.append({host:daq_amo_mon05,  id:'monreqsrv_psana_3', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 16 -n 32 -s '+max_evt_sz })
   #JBT
   #JBT# daq-amo-mon06 => subscribed to DSS03 and DSS06
   #JBT#   => mask = 4 + 32 = 36
   procmgr_config_mon.append({host:daq_amo_mon06,  id:'monreqsrv_psana_4', flags:'sp', cmd:pdsappRH7_path+'/monreqserver -P '+instrument+' -t psana -d -q 8 -i 36 -n 32 -s '+max_evt_sz })



procmgr_config = procmgr_config_base + procmgr_config_dss + procmgr_config_mon
