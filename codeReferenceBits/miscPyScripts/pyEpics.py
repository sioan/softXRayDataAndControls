import threading
import subprocess 

class dummyClass:
	 dummyVar1 = 0
	 
	 def __init__(self, VAL):
	 	self.VAL = VAL

def caget(pv):
	
	myString = subprocess.check_output(["caget","-t",pv])
	
	return float(myString)

def caput(pv,value):
	
	myString = subprocess.check_output(["caput",pv,str(value)])
	
	return
	
def update(myClass,myStdout):
	
	for line in iter(myStdout.readline, ''):
	
		myClass.VAL = float(line.split()[-1])
	
	return 0
	
	

def camonitor(pv):

	proc = subprocess.Popen(["camonitor", pv],stdout = subprocess.PIPE)
	
	myClass = dummyClass(1)
	
	t = threading.Thread(target = update,args = (myClass,proc.stdout))
	t.start()
	
	#return proc.stdout

	return myClass
