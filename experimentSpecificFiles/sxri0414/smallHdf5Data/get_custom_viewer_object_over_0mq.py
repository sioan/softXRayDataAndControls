import ctypes

my_custom_viewer_addresses = [id(i) for i in gc.get_objects() if str(type(i))=="<class 'dls.dls.dls_viewer'>"]

my_custom_viewer_object = ctypes.cast(my_custom_viewer_addresses[0],ctypes.py_object)
my_custom_viewer_object


