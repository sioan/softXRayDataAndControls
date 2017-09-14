def merge(d1, d2):
    for k in d2:
        if k in d1 and isinstance(d1[k], dict) and isinstance(d2[k], dict):
            merge(d1[k], d2[k])
        else:
            d1[k] = d2[k]   

def merge(d1, d2):
	

def merge_dicts(dict_list):
	"""
	Given any number of dicts, shallow copy and merge into a new dict,
	precedence goes to key value pairs in latter dicts.
	"""
	#print ("merging dictionary")
	result = {}
	#print("merging the dictionary list.")
	#print(dict_list)
	for dictionary in dict_list:
		#print dictionary
		result.update(dictionary)
	return result


