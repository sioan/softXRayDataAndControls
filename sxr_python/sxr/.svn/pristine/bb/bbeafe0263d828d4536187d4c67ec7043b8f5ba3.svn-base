# Constant Fraction Discriminator

import numpy as np
import matplotlib.pyplot as plt

def cfd(signal, fraction) :
    """
    Constant Fraction Discriminator (cfd)

    Signal: input signal
    Fraction: set fraction of edge
    
    returns a list of array positions that correspond to edges that at
    the same fraction of the signal    
    """

    # Subtract off 1.01*median value 
    # the extra 1% avoids noise fluctations giving false edges
    signal_sub = signal - 1.01 * np.median(signal)
    
    # Create scaled version of the signal
    scaled = signal_sub * fraction
    
    # subtract the delayed and scaled
    cfd_signal = signal_sub - scaled


    # Find edges
    edges_bool = cfd_signal > 0.0
    edges_bool_2 = np.logical_xor(edges_bool[1:],edges_bool[:-1])
    edge_index = np.where(edges_bool_2 == True)[0] 

    return edge_index
        

if __name__ == "__main__" :

    from sxr_mono_autofocus import FirstOrderSim
    xvals = np.arange(0.0,1000)
    spectrum = FirstOrderSim.projection(-0.4,xvals)
    
    edges = cfd(signal=spectrum, fraction=0.5)

    plt.clf()
    plt.plot(spectrum)
        
    for edge in edges :
        plt.axvline(edge, color="r", linestyle="solid")
    
    plt.grid()
    plt.draw()
    plt.show()
    
    #if edges.size%2 != 0 :
    #    print "odd number of edges",edges.size

    widths = edges[1::2] - edges[:-1:2]
    
    print widths
    print np.mean(widths), np.std(widths)


    
