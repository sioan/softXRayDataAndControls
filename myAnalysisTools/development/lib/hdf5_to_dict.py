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

def load_h5_file(file_name):

	if ('None'!=file_name):
		f = h5py.File(os.getcwd()+"/"+arg_dict['confg_file'],'r')
		this_dict= hdf5_to_dict(f)
		f.close()

	return this_dict

def write_dict_to_h5(file_name,data_dict):
	f = h5py.File(file_name+'.h5', 'w')	
		for i in data_dict:
			f.create_dataset(i, data=data_dict[i], chunks=True, maxshape=(None,))
	f.close()
