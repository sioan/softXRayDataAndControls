from common.detectors_pyami import IPIMBDetector as detector
import pyami
import os
PYPS_INTERACTIVE = os.getenv('PYPS_INTERACTIVE',"FALSE").lower()=='true'
if PYPS_INTERACTIVE:
  sxrgroup = 0xefff2400
  pyami.connect(sxrgroup)
else:
  print "WARNING: sxrdetectors.py, not interactive mode, not connecting ami"
  pass

class SxrDetectors(object):
  def __init__(self):
#     self.gas1   = detector("GDET:FEE1:241:ENRC","gas1",kind="gas")
#     self.gas2   = detector("GDET:FEE1:242:ENRC","gas1",kind="gas")
#     self.gas3   = detector("GDET:FEE1:361:ENRC","gas1",kind="gas")
#     self.gas4   = detector("GDET:FEE1:362:ENRC","gas1",kind="gas")
     self.neh2   = detector("NH2-SB1-IPM-01:FEX","neh2",kind="ipm")
     self.ipm1   = detector("SXR-IPM-01:FEX","ipm1",kind="ipm")
     self.dio1   = detector("SXR-DIO-01:FEX","dio1",kind="pim")
     self.ipm2   = detector("SXR-IPM-02:FEX","ipm2",kind="ipm")
     self.dio2   = detector("SXR-DIO-02:FEX","dio2",kind="pim")
     self.decmono  = detector("SXR-DEC-mono:FEX","dec-mono",kind="ipm")
     self.diomono  = detector("SXR-DIO-mono:FEX","dio-mono",kind="pim")
     self.ipmmono  = detector("SXR-IPM-mono:FEX","ipm-mono",kind="ipm")
#     self.ipm3m  = detector("SXR-IPM-03m:FEX","ipm3m",kind="ipm")
     self.dio3m  = detector("SXR-DIO-03m:FEX","dio3m",kind="pim")
     self.ipm3   = detector("SXR-IPM-03:FEX","ipm3",kind="ipm")
     self.dio3   = detector("SXR-DIO-03:FEX","dio3",kind="pim")
     self.ipm4   = detector("SxrBeamline-1|Ipimb-4","ipm4",kind="ipm")
     self.dio4   = detector("SxrBeamline-2|Ipimb-4","dio4",kind="pim")
     self.ipm5   = detector("SxrBeamline-1|Ipimb-5","ipm5",kind="ipm")
     self.dio5   = detector("SxrBeamline-2|Ipimb-5","dio5",kind="pim")
     self.diold1 = detector("SxrEndstation-0|Ipimb-0","diold1",kind="pim")
     self.diold2 = detector("SxrEndstation-0|Ipimb-1","diold2",kind="pim")

#     self.ipm1   = detector("HXX-UM6-IMB-01:FEX","ipm1",kind="ipm")
#     self.dio1   = detector("HXX-UM6-IMB-02:FEX","dio1",kind="pim")
#     self.ipm2   = detector("HFX-DG2-IMB-01:FEX","ipm2",kind="ipm")
#     self.dio2   = detector("HFX-DG2-IMB-02:FEX","dio2",kind="pim")
#     self.ipm3m  = detector("HFX-DG3-IMB-01:FEX","ipm3m",kind="ipm")
#     self.dio3m  = detector("HFX-DG3-IMB-02:FEX","dio3m",kind="pim")
#     self.ipm3   = detector("SXR-DG3-IMB-03:FEX","ipm3",kind="ipm")
#     self.dio3   = detector("SXR-DG3-IMB-04:FEX","dio3",kind="pim")
#     self.ipm4   = detector("SXR-SB1-IMB-01:FEX","ipm4",kind="ipm")
#     self.dio4   = detector("SXR-SB1-IMB-02:FEX","dio4",kind="pim")
#     self.ipm5   = detector("SXR-SB2-IMB-01:FEX","ipm5",kind="ipm")
#     self.dio5   = detector("SXR-SB2-IMB-02:FEX","dio5",kind="pim")
