#networking tools library
#first step is to load the netconfigfield into a dictionar

#filtering the list based on what has sxr, amo, or other relevant hutches.
#then automated pinging and making lists of what doesn't respond
def loadNetworkConfigSearchResults ():
	myDict = {}
	counter = 0
	f = open("netconfigSearchResults.txt")
	myReservedWords = ["PC Number","Ethernet Address","subnet","IP:","Contact","Location","Description"]	
	myKeyName = "nullName"
	myDict[myKeyName] = {}
	for line in f:
		#isKey = False
		#for myWord in myReservedWords:
		#	if myWord in line 
		

		#print(str(counter))
		#print(str(len(line.lstrip())))
		isName = len(line)-len(line.lstrip())
		if (isName == 0):
			myKeyName = line.split(":")[0]
			myDict[myKeyName]={}
			#print myKeyName
		else:
			myField = (line.split(":")[0]).lstrip()
			#myField = myField.split("\n")[0]
			#line[len(myField)+3:]
			if(len(myField)>1):
				myDict[myKeyName][myField] = line[len(myField)+3:]
			#myDict[myKeyName,myField]


		

	f.close()
	return myDict
