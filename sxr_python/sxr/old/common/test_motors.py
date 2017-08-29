import sxrbeamline

def test_motors():
    sx = sxrbeamline.diff.sx.wm()
    print "goniometer sample x is %.3f" % sx
    pass

