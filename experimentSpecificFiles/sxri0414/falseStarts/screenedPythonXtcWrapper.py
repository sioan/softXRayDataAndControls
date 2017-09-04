import os
import time
os.system("screen -d -m -S myPsanaScreen interactiveXtcExtractor.sh -e sxri0414 -r 63 -f 200 -s 4 -t")
#os.system("screen -d -m xtcExtractorFlagWrapper")

while(True):			#this is need to prevent lsf bsub from killing process 
	time.sleep(4)
