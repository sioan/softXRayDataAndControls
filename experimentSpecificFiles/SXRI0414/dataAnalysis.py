from pylab import *
import h5py
f = h5py.File("sxri0414run60.h5",'r')
#f = h5py.File("sxrx24615run21.h5",'r')
array(f)
#array(f['acqiris2'])
#array(f['acqiris2']).shape
#array(f[f.keys()[0]])
#array(f['andor']['1'])

def filterMaster(myDictionary,myMask):
	replacementDictionary = {}
	for i in myDictionary:
		print(str(myDictionary[i]))
		if ('dataset' in str(myDictionary[i])):
			print("dataset is in"+str(myDictionary[i]))
			if ('Summarized' not in str(myDictionary[i])):
				replacementDictionary[i] = myDictionary[i][array(myMask)]
			else:
				x=1	
		else:
			replacementDictionary[i] = {}
			print("dataset is not in"+str(myDictionary[i]))
			print(i)
			replacementDictionary[i] = filterMaster(myDictionary[i],myMask)

	return replacementDictionary

def filterMasterDictionary(myDictionary,myMask):
	replacementDictionary = {}
	for i in myDictionary:
		#print(str(myDictionary[i]))
		#if ('dataset' in str(myDictionary[i])):
		if (not isinstance(myDictionary[i],dict)):
			replacementDictionary[i] = myDictionary[i][array(myMask)]

		else:
			replacementDictionary[i] = {}
			#print("dataset is not in"+str(myDictionary[i]))
			print(i)
			replacementDictionary[i] = filterMasterDictionary(myDictionary[i],myMask)

	return replacementDictionary


#filter master with graphical interactive tool
#remove stuff not meaningful
#filter on by kicks

#linked graphics
#hist(array(f['GMD']),bins=400) #not fine enough near zero to filter on
#hist(array(f['acqiris2']),bins=400)
#hist(nan_to_num(array(f['gas_detector']['f_11_ENRC'])),bins=200)	#also on f_22_ENRC and permutation of 12

#event codes 
#162 is by kick
byKickMask = [bool((i+1)%2) for i in array(f['evr']['code_162'])]

#filtering on bykick works
newDictionary = filterMaster(f,byKickMask)

#shows mono efficiency
#plot(newDictionary['ebeam']['photon_energy'],newDictionary['GMD'],'.')
photonEnergyMask = array([(i<922 and i>906) for i in array(newDictionary['ebeam']['photon_energy'])])
newDictionaryB = filterMasterDictionary(newDictionary,photonEnergyMask)

f_11_enrcMask = array([(i<922 and i>0.8) for i in nan_to_num(array(newDictionary['gas_detector']['f_11_ENRC']))])

newDictionaryB = filterMasterDictionary(newDictionary,f_11_enrcMask)

#140 is beam and 120 Hz.  40  is independent of beam
#141 is beam and 60. Hz.  60  is independent of beam
#142 is beam and 30. Hz.  30  is independent of beam
#143 is beam and 10. Hz.  10  is independent of beam
#144 is beam and 5.0 Hz.  5.0 is independent of beam
#145 is beam and 1.0 Hz.  1.0 is independent of beam
#146 is beam and 0.5 Hz.  0.5 is independent of beam
#below are in colored sequencer event codes
#75 SXR Shutter open
#76 SXR Laser (On Time)
#77 SXR Laser (Delayed)
#78 SXR Mag Pol
#79 SXR Mag Trig
#80 SXR SlowCam Open
#81 SXR DAQ Readout

#break up data into smaller data bits
#create subsets based on 
#	1) unique EVR
#	2) position along scan i.e.(24845,49568,74291,99013,123736,148459,173182,197905,222627,247350
