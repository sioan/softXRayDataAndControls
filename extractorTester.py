#!/reg/g/psdm/sw/conda/inst/miniconda2-prod-rhel7/envs/ana-1.3.9/bin/python -i
from pylab import *
import h5py
import argparse
import sys
import IPython

def hdf5_to_dict(myhdf5Object):
	replacementDictionary = {}
	for i in myhdf5Object:
		print(str(myhdf5Object[i]))
		if ('dataset' in str(myhdf5Object[i])):
			print("dataset is in"+str(myhdf5Object[i]))
			if ('Summarized' not in str(myhdf5Object[i])):
				replacementDictionary[i] = nan_to_num(myhdf5Object[i])
			else:
				x=1	
		else:
			replacementDictionary[i] = {}
			print("dataset is not in"+str(myhdf5Object[i]))
			print(i)
			replacementDictionary[i] = hdf5_to_dict(myhdf5Object[i])

	return replacementDictionary

def main(fileName):
	#global myDict
	global my_dict
	#f = h5py.File("sxr10116run73.h5",'r')
	#f = h5py.File(fileName,'r')
	my_hdf5_object = h5py.File(fileName,'r')
	#f = h5py.File("sxrx24615run21.h5",'r')
	#for i in f:
	#	print(str(i))
	#	print(str(array(f[i])[:10]))
	#f.close()
	#myDict= hdf5_to_dict(f)

	#convert hdf5 to dict
	my_list = []
	def func(name, obj):
		my_list.append(name)

	my_hdf5_object.visititems(func)
	my_dict = {}
	
	for i in my_list:
		try:
			my_dict[i] = array(my_hdf5_object[i])
		except:
			#IPython.embed()
			pass

	my_hdf5_object.close()

if __name__ == '__main__':

	#myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
	print(sys.argv)	
	print("parsing arguments")
	myParser = argparse.ArgumentParser(description='Abstracts data analysis into user functions')
		
	
	myParser.add_argument('-f','--fileName',help='fileName',default="None")
	#myParser.add_argument('-dn','--group names',help='fileName',default="None")
	#myParser.add_argument('-sd','--group names',help='show data with group name',default="None")
	
	myArguments = myParser.parse_args()

	main(myArguments.fileName)
