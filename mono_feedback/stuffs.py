import time
from psp.Pv import Pv
import IPython
import numpy as np
from pylab import *

def ts_to_fid(timestamp):
    return 0x7FFF & timestamp[1]

def main():
    my_list = []
    
    for i in np.arange(10):
        x,y,dydx = get_slope()
        my_list.append([x,y,dydx])
        print(str(x)+", "+str(y)+", "+str(dydx))

    my_list=array(my_list)
    IPython.embed()

def get_slope():
    try:
        sample_time = 0.50
        num_to_show = 5
        gdet = Pv('GDET:FEE1:241:ENRC')
        gmd = Pv('SXR:GMD:BLD:milliJoulesPerPulse')
        ebeam = Pv('BLD:SYS0:500:PHOTONENERGY')

        pv_list = [gdet, gmd, ebeam]

        for pv in pv_list:
            pv.monitor_start(True)
        time.sleep(sample_time)
        for pv in pv_list:
            pv.monitor_stop()

        my_dict = {}

        for pv in pv_list:
            for my_timestamps, my_vals in zip(pv.timestamps, pv.values):
                if ts_to_fid(my_timestamps) in my_dict:
                    my_dict[ts_to_fid(my_timestamps)][pv.name] = my_vals
                else:
                    my_dict[ts_to_fid(my_timestamps)] = {pv.name:my_vals}

        #matches = 0
        #for key, val in my_dict.iteritems():
        #    if len(val) == 3:
	    #        matches += 1
        #print "num matches %d"%matches

        #for pv in pv_list:
        #    print "Showing first %d fids of %s"%(num_to_show, pv.name)
        #    for i in range(num_to_show):
        #        print "%d: %f"%(ts_to_fid(pv.timestamps[i]), pv.values[i])

        #my_array = np.array([np.array([my_dict[i][j] for j in my_dict[i]]) for i in my_dict])
        my_array = np.array([np.array([my_dict[i][j] for j in my_dict[i]]) for i in my_dict if len(my_dict[i])==3])

        normalized_mono = my_array[1]/my_array[0]

        my_cov = np.cov(np.array([my_array[2],normalized_mono]))

        my_slope = my_cov[0,1]/my_cov[0,0]

        return np.mean(my_array[2]), np.mean(normalized_mono),my_slope

    except:
        IPython.embed()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
