import pypsepics

class EVReventCode:
	""" This class is to manipulate the assignment of different event codes
	to different output triggers"""

	def __init__(self,ioc="XPP:R31:EVR:21"):
		self.ioc=ioc
		self.__nevent_numbers = 14
		self.__ntriggers = 10

	def __getpvnames(self,event):
		ret = dict()
		ret["enable"]    = self.ioc + ":EVENT%dCTRL.ENAB" % event
		ret["eventcode"] = self.ioc + ":EVENT%dCTRL.ENM" % event
		for i in range(self.__ntriggers):
			ret[i] = self.ioc + ":EVENT%dCTRL.OUT%d" % (event,i)
		ret["irq"] = self.ioc + ":EVENT%dCTRL.VME" % event
		ret["count"] = self.ioc + ":EVENT%dCNT" % event
		ret["rate"] = self.ioc + ":EVENT%dRATE" % event
		return ret

	def enable(self,event_number,trigger):
		names = self.__getpvnames(event_number)
		pypsepics.put(names["enable"],1)
		pypsepics.put(names[trigger],1)
		pypsepics.put(names["irq"],1)

	def disable(self,event_number,trigger):
		names = self.__getpvnames(event_number)
		pypsepics.put(names[trigger],0)
		pypsepics.put(names["irq"],0)

	def setEventCodeForEventNumber(self,event_number,event_code):
		names = self.__getpvnames(event_number)
		pypsepics.put(names["eventcode"],event_code)

	def setDefaults(self):
		default_codes = (140,141,142,143,144,145,40,41,42,43,44,45,83,84)
		for i in range(self.__nevent_numbers):
			names = self.__getpvnames(event=i+1); # starts with 1 and not zero
			pypsepics.put(names["eventcode"],default_codes[i])
			pypsepics.put(names["enable"],1)
			for i in range(self.__ntriggers):
				self.disableAllEventsForGivenTrigger(i)
			pypsepics.put(names["irq"],0)

	def setDefaultsForTrigger(self,trigger):
		default_codes = (140,141,142,143,144,145,40,41,42,43,44,45,83,84)
		for i in range(self.__nevent_numbers):
			names = self.__getpvnames(event=i+1); # starts with 1 and not zero
			pypsepics.put(names["eventcode"],default_codes[i])
			pypsepics.put(names["enable"],1)
			self.disableAllEventsForGivenTrigger(trigger)
			pypsepics.put(names["irq"],0)

	def disableAllEventsForGivenTrigger(self,trigger):
		""" Disable all events code for a give  trigger """
		if (trigger>self.__ntriggers-1):
			print "in disableAllEventsForGivenTrigger you asked for a trigger that is not defined ... exiting"
			return 0
		for i in range(self.__nevent_numbers):
			names = self.__getpvnames(i+1); # starts with 1 and not zero
			pypsepics.put(names[trigger],0)
		return 1

class ControlEVR:
	""" Control EVR
	32 bit delay and width
	15 bit prescaler
	119MHz clock"""
	def __init__(self,ioc="XPP:R31:EVR:21",trigger=0):
		self.ioc = ioc
		self.trigger = trigger
		self.__names = {
			'state'    : "E",
			'enable'   : "E",
			'polarity' : "P",
			'width'    : "W",
			'delay'    : "D",
			'prescale' : "C"
		}
		# max delay,width = 32 bit
		# max prescaler = 15 bit
		self.EVReventCode = EVReventCode(self.ioc)
		self.__ntriggers = self.EVReventCode._EVReventCode__ntriggers

	def setDefaultsForTrigger(self,trigger):
		""" Set EVR defaults for a given trigger (including mapping trigger#i->out#i"""
		self.EVReventCode.setDefaultsForTrigger(trigger)
		pypsepics.put(self.ioc+":CTRL.ENAB",1); #enable card
		self.assignOutToTrigger(trigger,trigger); # assign out #i to trigger #i
		self.change("enable",1,trigger); # enable trigger #i
		self.change("polarity",0,trigger); # polarity normal for trigger #i
		self.change("prescale",1,trigger); # default prescaler for trigger #i
		self.setWidth(1e-3,trigger)
		self.setDelay(1e-3,trigger)

	def setDefaults(self):
		self.EVReventCode.setDefaults()
		pypsepics.put(self.ioc+":CTRL.ENAB",1); #enable card
		for i in range(self.__ntriggers):
			self.assignOutToTrigger(i,i); # assign out #i to trigger #i
		for i in range(self.__ntriggers):
			self.change("enable",1,i); # enable trigger #i
			self.change("polarity",0,i); # polarity normal for trigger #i
			self.change("prescale",1,i); # default prescaler for trigger #i
			self.setWidth(1e-3,i)
			self.setDelay(1e-3,i)

	def assignOutToTrigger(self,out,trigger):
		pvname = self.ioc + ":CTRL.FPS%d" % out
		pypsepics.put(pvname,trigger); #assign out 0 to trigger 0

	def disableAllEventsForGivenTrigger(self,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		self.EVReventCode.disableAllEventsForGivenTrigger(trigger)

	def __getpvname(self,what,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		ret = "%s:CTRL.DG%d%s" % (self.ioc,trigger,self.__names[what])
		return ret

	def change(self,what,value,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		#print what,value,pvname
		pvname = self.__getpvname(what,trigger)
		pypsepics.put(pvname,value)

	def get(self,what,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		pvname = self.__getpvname(what,trigger)
		return pypsepics.get(pvname)

	def enable(self,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		self.change("enable",1,trigger)

	def isEnable(self,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		return self.get("enable",trigger)


	def setPrescale(self,value,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		self.change("prescale",int(value),trigger)

	def getPrescale(self,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		return self.get("prescale",trigger)

	def setWidth(self,value,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		prescale = self.getPrescale(trigger)
		timebase = 1./(119e6/prescale)
		self.change("width",int(value/timebase),trigger)

	def getWidth(self,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		prescale = self.getPrescale(trigger)
		timebase = 1./(119e6/prescale)
		return self.get("width",trigger)*timebase

	def setDelay(self,value,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		prescale = self.getPrescale(trigger)
		timebase = 1./(119e6/prescale)
		self.change("delay",int(value/timebase),trigger)

	def getDelay(self,trigger=None):
		if (trigger is None):
			trigger = self.trigger
		prescale = self.getPrescale(trigger)
		timebase = 1./(119e6/prescale)
		return self.get("delay",trigger)*timebase
