#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/ipython
import argparse
import sys

#example usage to call script
#ipython -i interactivePythonTestArgParsed.py -- -f haGotTheFile.h5

def main(myFile):
	print("in main")
	print(myFile)

if __name__ == '__main__':

	print("testing argument passing for ipython")
	print("here's the sent arguments"+str(sys.argv))

	myParser = argparse.ArgumentParser(description='Generating a config file for analysis')
	#myGroup = myParser.add_mutually_exclusive_group()
	
	myParser.add_argument('-f','--file', help='filename')

	myArguments = myParser.parse_args()
	
	x=1	
	main(myArguments.file)
