#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel6/envs/ana-1.3.37/bin/python
from smtplib import SMTP
import datetime
from pyEpics import *
import time
import socket

#bash command
#echo "Subject: sendmail test" | sendmail -v sioan@slac.stanford.edu

debuglevel = 0
smtp = SMTP()
smtp.set_debuglevel(debuglevel)

from_addr = "amoopr@slac.stanford.edu"
to_addr = ["jaldrich@slac.stanford.edu","sstubbs@slac.stanford.edu","pwalter@slac.stanford.edu"]
#to_addr = ["sstubbs@slac.stanford.edu"]
while(True):
    try:
        #Crashed with smtp connection stuff outside of the loop. Let's try it inside
        smtp.connect('psmail.pcdsn', 25)

        myPvs =["AMO:LMP:PTM:10:AT_SPD","AMO:LMP:PTM:11:AT_SPD","AMO:LMP:PTM:20:AT_SPD","AMO:LMP:PTM:30:AT_SPD","AMO:LMP:PTM:31:AT_SPD","AMO:LMP:PTM:32:AT_SPD","AMO:LMP:PTM:33:AT_SPD","AMO:LMP:PTM:40:AT_SPD","AMO:LMP:PTM:41:AT_SPD","AMO:LMP:VG:21:PRESS","AMO:LMP:VG:30:PRESS"]
        subj = "AMO bi-hourly bake status update"
        message_text = ""
        for i in myPvs:

            message_text+=i+" = "+cagetg(i)+"\n"

        message_text+="Running on host %s" % socket.gethostname()
        date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( from_addr, to_addr, subj, date, message_text )

        smtp.sendmail(from_addr, to_addr, msg)
        print(msg)

        smtp.quit()
        #send every two hours
        time.sleep(2*60.0*60.0)
        #time.sleep(10)

    except KeyboardInterrupt:
        break

