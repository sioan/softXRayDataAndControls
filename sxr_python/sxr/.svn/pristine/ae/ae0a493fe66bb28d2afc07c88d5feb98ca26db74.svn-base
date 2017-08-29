import telnetlib
import time

tn = telnetlib.Telnet()
tn.open("digi-sxr-01",2011)

print "DISPLAY OFF"
tn.write("DISP OFF\n")

time.sleep(5)

print "DISPLAY ON"
tn.write("DISP ON\n")

print "VOLTAGE/CURRENT"
tn.write("VOLT?\n")
print tn.read_until("\n")


tn.write("CURR?\n")
print tn.read_until("\n")




