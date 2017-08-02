#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python
import argparse
import sys
import subprocess

def main(rawArguments):
	print("entering main function")
	myWorkingDirectory = subprocess.check_output("pwd")
	print("working directory = "+myWorkingDirectory)
	

if __name__ == '__main__':
	
	rawArguments = sys.argv
	print rawArguments
	
	"""
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	myParser.add_argument('-l','--list', help='show screens instances logged in database')
	myParser.add_argument('-r','--run',type=int,help='the run number to use when running offline')
	myParser.add_argument('-c','--configFile',help='the config file to write to')
	myParser.add_argument('-hd5','--hd5File',help='the small data file to write to')
	myParser.add_argument('-t','--testSample',action='store_true',help='only take a small set of data for testing')

	myArguments = myParser.parse_args()
	print("arguments parsed")"""

	#main(myArguments.list)
	main(rawArguments)
