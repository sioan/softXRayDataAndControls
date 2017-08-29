#!/usr/bin/env python

iSeqId               = 2

pvBeamRate           = "EVNT:SYS0:1:LCLSBEAMRATE"
pvBurstTestRate      = "PATT:SYS0:1:TESTBURSTRATE"
pvBurstTestUseBeam   = "PATT:SYS0:1:TESTBURST.N"

#PATT:SYS0:1:TESTBURSTRATE
#PATT:SYS0:1:TESTBURST.N 524288

#mcc_seq_ioc_prefix   = "IOC:IN20:EV01:"
#mcc_seq_ioc_prefix   = "IOC:IN20:EV01:ECS"
mcc_seq_ioc_prefix   = "ECS:SYS0:"

pvBeamOwner          = mcc_seq_ioc_prefix  + "0:BEAM_OWNER_ID"
pvBeamOwnername      = mcc_seq_ioc_prefix  + "0:BEAM_OWNER_NAME"

mcc_seq_seq_prefix   = mcc_seq_ioc_prefix + "%d:" % (iSeqId)

pvHutchId            = mcc_seq_seq_prefix + "HUTCH_ID"      
pvHutchName          = mcc_seq_seq_prefix + "HUTCH_NAME"      
pvSeqEvent           = mcc_seq_seq_prefix + "SEQ.A"  # Event Codes
pvSeqBeamDelay       = mcc_seq_seq_prefix + "SEQ.B"  # Beam Delays
pvSeqFiduDelay       = mcc_seq_seq_prefix + "SEQ.C"  # Fiducial Delays
pvSeqBurst           = mcc_seq_seq_prefix + "SEQ.D"  # Burst Counts. -1: forever, -2: stop
pvSeqUpdate          = mcc_seq_seq_prefix + "SEQ.PROC" 
pvSeqLen             = mcc_seq_seq_prefix + "LEN"      
pvPlayCtrl           = mcc_seq_seq_prefix + "PLYCTL" # 0: Stop,    1: Play
pvPlayStat           = mcc_seq_seq_prefix + "PLSTAT" # 0: Stopped, 1: Waiting,  2: Playing
pvPlayMode           = mcc_seq_seq_prefix + "PLYMOD" # 0: Once,    1: Repeat N, 2: Repeat Forever
pvRepCount           = mcc_seq_seq_prefix + "REPCNT"
pvSeqStatus          = mcc_seq_seq_prefix + "ERRTYP"
pvSeqErrorIndex      = mcc_seq_seq_prefix + "ERRIDX"
pvPlayCount          = mcc_seq_seq_prefix + "PLYCNT"
pvPlayTotalCount     = mcc_seq_seq_prefix + "TPLCNT"
pvPlayCurStep        = mcc_seq_seq_prefix + "CURSTP"
pvMccSeqSyncMarker   = mcc_seq_seq_prefix + "SYNCMARKER"   # 0:0.5 1:1 2:5 3:10 4:30 5:60 6:120 7:360
pvMccSeqBeamRequest  = mcc_seq_seq_prefix + "BEAMPULSEREQ" # 0: TimeSlot 1: Beam

dictRateToSyncMarker = {0.5:0, 1:1, 5:2, 10:3, 30:4, 60:5, 120:6, 360:7}
dictSyncMarkerToRate = {0:0.5, 1:1, 2:5, 3:10, 4:30, 5:60, 6:120, 7:360}

# event code owner
# mcc_seq_ioc_prefix   + "0:EC_" + event_code + "_OWNER_ID"

#local_seq_ioc_prefix = "AMO:R12:IOC:SEQ:"
#local_seq_ioc_prefix = "SXR:R24:IOC:22:EV:"
#local_seq_ioc_prefix = "IOC:MEC:EVENTSEQUENCER:"
#local_seq_event_num  = 20
#pvLocSeqEventPre     = local_seq_ioc_prefix + "EC_%d:"    % (iSeqId)
#pvLocSeqBeamDelayPre = local_seq_ioc_prefix + "BD_%d:"    % (iSeqId)
#pvLocSeqFiduDelayPre = local_seq_ioc_prefix + "FD_%d:"    % (iSeqId)

pvMccBurstCtrl       = "PATT:SYS0:1:MPSBURSTCTRL"
pvMccBurstNumShot    = "PATT:SYS0:1:MPSBURSTCNTMAX"
pvMccBurstRate       = "PATT:SYS0:1:MPSBURSTRATE"  # 0:Full 1:30 2:10 3:5 4:1 5:0.5 6:pattern 7:off
pvMccBurstCount      = "PATT:SYS0:1:MPSBURSTCNT"
pvMccBurstReqBykik   = "IOC:BSY0:MP01:REQBYKIKBRST"
pvMccBurstReqPoc     = "IOC:BSY0:MP01:REQPCBRST"
pvMccBykikEnable     = "IOC:IN20:EV01:BYKIK_ABTACT"
PvMccBykikPeriod     = "IOC:IN20:EV01:BYKIK_ABTPRD"

pvMccTestBurstDep    = "PATT:SYS0:1:TESTBURST.N"   # Set to 0 to elminate dependency on beam
pvMccTestBurstRate   = "PATT:SYS0:1:TESTBURSTRATE" # 0:Full 1:30 2:10 3:5 4:1 5:0.5 6:pattern 7:off

seqGroupMin = [0, 67, 75, 90, 83, 183, 167]
seqGroupMax = [0, 70, 80, 98, 89, 183, 182]
seqEventMin = seqGroupMin[iSeqId]
seqEventMax = seqGroupMax[iSeqId]
