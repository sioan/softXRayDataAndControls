#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel6/envs/ana-1.3.37/bin/python
from smtplib import SMTP
import datetime
from pyEpics import *
import time

#bash command
#echo "Subject: sendmail test" | sendmail -v sioan@slac.stanford.edu

debuglevel = 0

smtp = SMTP()
smtp.set_debuglevel(debuglevel)
smtp.connect('psmail.pcdsn', 25)
#ismtp.login('amoopr@slac.stanford.edu', '')

from_addr = "amoopr@slac.stanford.edu"
#to_addr = "sioan@slac.stanford.edu,pwalter@slac.stanford.edu,sstubbs@slac.stanford.edu"
#to_addr = "sioan@slac.stanford.edu, sstubbs@slac.stanford.edu"
to_addr = ["sioan@slac.stanford.edu","sstubbs@slac.stanford.edu","pwalter@slac.stanford.edu"]

while(True):
    try:	
        myPvs =["AMO:LMP:PTM:10:AT_SPD","AMO:LMP:PTM:11:AT_SPD","AMO:LMP:PTM:20:AT_SPD","AMO:LMP:PTM:30:AT_SPD","AMO:LMP:PTM:31:AT_SPD","AMO:LMP:PTM:32:AT_SPD","AMO:LMP:PTM:33:AT_SPD","AMO:LMP:PTM:40:AT_SPD","AMO:LMP:PTM:41:AT_SPD","AMO:LMP:VG:21:PRESS"]
        subj = "AMO bake status update"
        message_text = ""
        for i in myPvs:

            message_text+=i+" = "+cagetg(i)+"\n"

        date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )

        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( from_addr, to_addr, subj, date, message_text )

        smtp.sendmail(from_addr, to_addr, msg)
        print(msg)
        #time.sleep(15.0*60.0)
        time.sleep(10)

    except KeyboardInterrupt:
        break

smtp.quit()
