x = array([])
y = array([])

for i in myApdGmdDict.keys():
	x = append(x,float(i))
	if(myApdGmdDictCounter[i]!=0):
		y = append(y,myApdGmdDict[i]*1.0/myApdGmdDictCounter[i])
	else:
		y = append(y,0)
