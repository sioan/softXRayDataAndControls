import ctypes
import gc

my_custom_viewer_addresses = [id(i) for i in gc.get_objects() if str(type(i))=="<class 'dls.dls.dls_viewer'>"]

my_custom_viewer_object = ctypes.cast(my_custom_viewer_addresses[0],ctypes.py_object)
my_custom_viewer_object


myKeys = list(my_custom_viewer_object.value.my_subsets.keys())[0]
this_custom_viewer  = my_custom_viewer_object.value.my_subsets[myKeys]
#my_custom_viewer_object.value.widget.offset='0'	#changes widget. how to change widget from custom viewer code?

