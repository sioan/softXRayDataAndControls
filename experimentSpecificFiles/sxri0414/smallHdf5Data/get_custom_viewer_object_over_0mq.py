import ctypes
import gc

#my_custom_viewer_addresses = [id(i) for i in gc.get_objects() if str(type(i))=="<class 'dls.dls.dls_viewer'>"]
my_custom_viewer_addresses = [id(i) for i in gc.get_objects() if str(type(i))=="<class 'dls.dls_no_offset.dls_viewer'>"]

my_custom_viewer_object = ctypes.cast(my_custom_viewer_addresses[0],ctypes.py_object)
my_custom_viewer_object


#myKeys = list(my_custom_viewer_object.value.my_subsets.keys())[0]
#this_custom_viewer  = my_custom_viewer_object.value.my_subsets[myKeys]
#this_custom_viewer  = my_custom_viewer_object.value
#my_custom_viewer_object.value.widget.offset='0'	#changes widget. how to change widget from custom viewer code?


################
################
#this allows for changing the Subsets widget in data collection

#type(this_custom_viewer.last_chosen_id)
#myStyle = ctypes.cast(0x7f18512eb588,ctypes.py_object)	#copied and pasted from memory address one line above
#myStyle.value.markersize
#myStyle.value.markersize=1
#myStyle.value.markersize
#myStyle.value.markersize=7
#myStyle.value.parent
#mySubsetGroup = ctypes.cast(0x7f18513eef60,ctypes.py_object) #copied and pasted from memory address one line above 
#mySubsetGroup.value.label
#mySubsetGroup.value.label = 'testing'
#mySubsetGroup.value.label = 'Subset 2'

################
################
#this identifies it in the layer state
#temp = application.viewers[0][1]
#temp
#temp.selected_layer
#temp.selected_layer
