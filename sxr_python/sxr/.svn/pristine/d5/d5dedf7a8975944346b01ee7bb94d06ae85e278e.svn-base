from smartMotor import SmartMotor
from scan import AScan, DScan, A2Scan, D2Scan

def foo(scan):
    print scan.get_position()
    pass

m1 = SmartMotor("SXR:USR:MMS:21")
m2 = SmartMotor("SXR:USR:MMS:22")

sa = AScan(m1, -2, 2, 4)
sa.set_post_move_hook(foo)

sd = DScan(m1, -2, 2, 4)
sd.set_post_move_hook(foo)

def scan2print(scan):
    print "position: %6.3f\t%6.3f" % (m1.get_position(), m2.get_position())
    pass

sa2 = A2Scan(m1, -5, 5, 2, m2, -5, 5, 2)
sa2.set_post_move_hook(scan2print)

sd2 = D2Scan(m1, -5, 5, 2, m2, -5, 5, 2)
sd2.set_post_move_hook(scan2print)
