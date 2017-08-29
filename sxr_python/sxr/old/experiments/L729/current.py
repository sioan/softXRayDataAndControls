
from device import Device
import sxrmotors

pvBase = None
sxrmotors = sxrmotors.SXRMotors()
class USER(Device):
    def __init__(self,
		   diamondx = sxrmotors.user_mmn_02,
                   diamondy = sxrmotors.user_mmn_01,
                   specphi = sxrmotors.user_mmn_03,
                   speczoom = sxrmotors.user_dumb_32,
                   specfocus = sxrmotors.user_dumb_31,
                   yagzoom = sxrmotors.user_dumb_29,
                   yagfocus = sxrmotors.user_dumb_30,
                   cspadx = sxrmotors.user_mmn_05,
                   objName = "madsen",
                   presetsfile = "/reg/neh/operator/sxropr/sxrpython_data/L729_presets.py"):
        Device.__init__(self,objName,pvBase,presetsfile)
        self.diamondx=diamondx
        self.diamondy=diamondy
        self.specphi=specphi
        self.speczoom=speczoom
        self.specfocus=specfocus
        self.yagzoom=yagzoom
        self.yagfocus=yagfocus
        self.cspadx=cspadx

        self.motors = {
            "diamondx": diamondx,
            "diamondy": diamondy,
            "specphi": specphi,
            "speczoom": speczoom,
            "specfocus": specfocus,
            "speczoom": yagzoom,
            "specfocus": yagfocus,
            "cspadx": cspadx
            }
        pass

    pass

