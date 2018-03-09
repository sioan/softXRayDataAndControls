def setAlarm(PV,alarmLevel,highOrLow):
        '''Takes PV and checks if alert should be sent - needs to be told if level is "high" or "low"'''
        if highOrLow == "high":
                return cagetg(PV) > alarmLevel
        elif highOrLow == "low":
                return cagetg(PV) < alarmLevel
