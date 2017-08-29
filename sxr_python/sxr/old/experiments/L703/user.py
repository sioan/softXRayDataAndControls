from common.device import Device
import sxrmotors
import math
import time
from common import virtualmotor, pypsepics
from common.smartactpiezo import SaPiezo

pvBase = None
sxrmotors = sxrmotors.SXRMotors()
class USER(Device):
    def __init__(self,
                 elog=None,
                 jet_x = sxrmotors.user_ims_01,
                 cam2_focus = sxrmotors.user_ims_03,
                 cam2_zoom = sxrmotors.user_ims_04,
	         jet_z = sxrmotors.user_ims_05,
		 cam1_x = sxrmotors.user_ims_06,
		 cam1_y = sxrmotors.user_ims_07,
                 cam1_z = sxrmotors.user_ims_08,
                 jet_y = sxrmotors.user_ims_09,
                 cam3_x = sxrmotors.user_ims_10,
                 cam3_y = sxrmotors.user_ims_11,
                 cam3_z = sxrmotors.user_ims_12,
                 mir_y = sxrmotors.user_ims_13,
                 cam2_x = sxrmotors.user_ims_14,
		 cam2_y = sxrmotors.user_ims_15,
                 cam2_z = sxrmotors.user_ims_16,
                 cam3_focus = sxrmotors.user_dumb_29,
                 cam3_zoom = sxrmotors.user_dumb_30,
		 cam1_focus = sxrmotors.user_dumb_31,
                 cam1_zoom = sxrmotors.user_dumb_32,
                 objName = "L703_Gruebel",
                 presetsfile = "/reg/neh/operator/sxropr/sxrpython_data/L703_Gruebel_presets.py"):
        Device.__init__(self,objName,pvBase,presetsfile)

        self.elog = elog
        self.jet_x = jet_x
        self.cam2_focus = cam2_focus
        self.cam2_zoom = cam2_zoom
        self.jet_z = jet_z
        self.cam1_x = cam1_x
        self.cam1_y = cam1_y
        self.cam1_z = cam1_z
        self.jet_y = jet_y
        self.cam3_x = cam3_x
        self.cam3_y = cam3_y
        self.cam3_z = cam3_z
        self.mir_y = mir_y
        self.cam2_x = cam2_x
        self.cam2_y = cam2_y
        self.cam2_z = cam2_z
        self.cam3_focus = cam3_focus
        self.cam3_zoom = cam3_zoom
        self.cam1_focus = cam1_focus
        self.cam1_zoom = cam1_zoom

        self.cam3_h = virtualmotor.VirtualMotor(motorsobj = sxrmotors,
                                                name = "cam3_h",
                                                move = self._move_cam3h,
                                                wm = self._wm_cam3h,
                                                wait = self._wait_cam3,
                                                get_ulowlim = self._get_ulowlim_cam3h,
                                                get_uhilim = self._get_uhilim_cam3h,
                                                egu="mm"
                                                )

        self.cam3_v = virtualmotor.VirtualMotor(motorsobj = sxrmotors,
                                                name = "cam3_h",
                                                move = self._move_cam3v,
                                                wm = self._wm_cam3v,
                                                wait = self._wait_cam3,
                                                get_ulowlim = self._get_ulowlim_cam3v,
                                                get_uhilim = self._get_uhilim_cam3v,
                                                egu="mm"
                                                )

        self.mir_xfine = SaPiezo(sxrmotors, "mir_xfine", "SXR:SDC:PZM:02")
        self.jet_yfine = SaPiezo(sxrmotors, "jet_yfine", "SXR:SDC:PZM:01")
                                                
	
        self.motors = {
            "jet_x": jet_x,
            "cam2_focus": cam2_focus,
            "cam2_zoom": cam2_zoom,
            "jet_z": jet_z,
            "cam1_x": cam1_x,
            "cam1_y": cam1_y,
            "cam1_z": cam1_z,
            "jet_y": jet_y,
            "cam3_x": cam3_x,
            "cam3_y": cam3_y,
            "cam3_z": cam3_z,
            "mir_y": mir_y,
            "cam2_x": cam2_x,
            "cam2_y": cam2_y,
            "cam2_z": cam2_z,
            "cam3_focus": cam3_focus,
            "cam3_zoom": cam3_zoom,
            "cam1_focus": cam1_focus,
            "cam1_zoom": cam1_zoom,
            "cam3_h": self.cam3_h,
            "cam3_v": self.cam3_v,
            "mir_xfine": self.mir_xfine,
            "jet_yfine": self.jet_yfine
            }
        pass

    def _get_uhilim_cam3h(self):
        return self.__cam3h_from_xy(self.cam3_x.get_lowlim(), self.cam3_y.get_hilim())
        pass

    def _get_ulowlim_cam3h(self):
        return self.__cam3h_from_xy(self.cam3_x.get_hilim(), self.cam3_y.get_lowlim())
        pass

    def _get_uhilim_cam3v(self):
        return self.__cam3v_from_xy(self.cam3_x.get_hilim(), self.cam3_y.get_hilim())
        pass

    def _get_ulowlim_cam3v(self):
        return self.__cam3v_from_xy(self.cam3_x.get_lowlim(), self.cam3_y.get_lowlim())
        pass

    def _move_cam3h(self,pos):
        sqrt2 = math.sqrt(2)
        xnew = -pos/sqrt2
        ynew = pos/sqrt2
        self.cam3_x.mv(xnew)
        self.cam3_y.mv(ynew)
        pass

    def _move_cam3v(self, pos):
        sqrt2 = math.sqrt(2)
        xnew = pos/sqrt2
        ynew = pos/sqrt2
        self.cam3_x.mv(xnew)
        self.cam3_y.mv(ynew)
        pass

    def __cam3h_from_xy(self,x,y):
        #return math.sqrt(2)*(-x+y)
        return y*math.cos(math.pi/4) - x*math.sin(math.pi/4)

    def __cam3v_from_xy(self,x,y):
        #return math.sqrt(2)*(x+y)
        return y*math.sin(math.pi/4) + x*math.cos(math.pi/4)

    def _wm_cam3h(self):
        return self.__cam3h_from_xy(self.cam3_x.wm(), self.cam3_y.wm())

    def _wm_cam3v(self):
        return self.__cam3v_from_xy(self.cam3_x.wm(), self.cam3_y.wm())

    def _wait_cam3(self):
        self.cam3_x.wait()
        self.cam3_y.wait()
        pass

    def __dumb_wait(self,channel,val):
        while pypsepics.get(channel) != val:
            time.sleep(.1)
            pass
        pass

    def __str_from_arr(self,arr):
        s=""
        for i in range(len(arr)):
            if arr[i] == 0:
                break
            s+=chr(arr[i])
            pass
        return s

    def log_images(self,message="L703 camera images"):
        if self.elog is None:
            print "Elog not defined, sorry!"
            return
        
        cam1next = pypsepics.get("SXR:GIGE:CAM:703:1:JPEG:FileNumber")
        cam2next = pypsepics.get("SXR:GIGE:CAM:703:2:JPEG:FileNumber")
        cam3next = pypsepics.get("SXR:GIGE:CAM:703:3:JPEG:FileNumber")
        
        pypsepics.put("SXR:GIGE:CAM:703:1:JPEG:NumCapture",1)
        pypsepics.put("SXR:GIGE:CAM:703:2:JPEG:NumCapture",1)
        pypsepics.put("SXR:GIGE:CAM:703:3:JPEG:NumCapture",1)

        print "capturing..."
        pypsepics.put("SXR:GIGE:CAM:703:1:JPEG:Capture",1)
        pypsepics.put("SXR:GIGE:CAM:703:2:JPEG:Capture",1)
        pypsepics.put("SXR:GIGE:CAM:703:3:JPEG:Capture",1)

        print "waiting..."
        self.__dumb_wait("SXR:GIGE:CAM:703:1:JPEG:FileNumber",cam1next+1)
        self.__dumb_wait("SXR:GIGE:CAM:703:2:JPEG:FileNumber",cam2next+1)
        self.__dumb_wait("SXR:GIGE:CAM:703:3:JPEG:FileNumber",cam3next+1)

        f1 = self.__str_from_arr(pypsepics.get("SXR:GIGE:CAM:703:1:JPEG:FullFileName_RBV"))
        f2 = self.__str_from_arr(pypsepics.get("SXR:GIGE:CAM:703:2:JPEG:FullFileName_RBV"))
        f3 = self.__str_from_arr(pypsepics.get("SXR:GIGE:CAM:703:3:JPEG:FullFileName_RBV"))

        print f1
        print f2
        print f3

        print "logging..."
        self.elog.submit(text=message,
                         file=f1,
                         file_descr="cam1: %s" % ("/reg/d/psdm/sxr/sxr70313/usr/"+f1.split("/")[-1])
                         )
        self.elog.submit(text=message,       
                         file=f2,
                         file_descr="cam2: %s" % ("/reg/d/psdm/sxr/sxr70313/usr/"+f2.split("/")[-1])
                         )
        self.elog.submit(text=message,
                         file=f3,
                         file_descr="cam3: %s" % ("/reg/d/psdm/sxr/sxr70313/usr/"+f3.split("/")[-1])
                         )
        print "done!"
        

    def capture_images(self,nImages):
        if nImages > 100:
            print "Max 100 images, aborting"
            return
            pass

        pypsepics.put("SXR:GIGE:CAM:703:1:JPEG:NumCapture",nImages)
        pypsepics.put("SXR:GIGE:CAM:703:2:JPEG:NumCapture",nImages)
        pypsepics.put("SXR:GIGE:CAM:703:3:JPEG:NumCapture",nImages)

        for i in range(1,4):
            name = pypsepics.get("SXR:GIGE:CAM:703:%d:JPEG:FileName_RBV" % i)
            #form = pypsepics.get("SXR:GIGE:CAM:703:%d:JPEG:FileTemplate_RBV" % i)
            next = pypsepics.get("SXR:GIGE:CAM:703:%d:JPEG:FileNumber" % i)
            #print form
            #import sys
            #sys.stdout.flush()
            #f1 = form % ("",name,next)
            #print "Capturing %d images for cam%d: beginning with %s" % (nImages,f1)
            print "Capturing %d images for cam%d: beginning with image-# %04d" % (nImages,i,next)
            pass
        
        pypsepics.put("SXR:GIGE:CAM:703:1:JPEG:Capture",1)
        pypsepics.put("SXR:GIGE:CAM:703:2:JPEG:Capture",1)
        pypsepics.put("SXR:GIGE:CAM:703:3:JPEG:Capture",1)

        pass
        
            
    pass
