from pylab import *
import h5py
#print("importing hdf5_to_dict")
def hdf5_to_dict(myhdf5Object):
	replacementDictionary = {}
	myList = []
	myhdf5Object.visit(myList.append)
	for i in myList:
		try:
			replacementDictionary[i] = array(myhdf5Object[i])
		except:
			pass
		

	return replacementDictionary
