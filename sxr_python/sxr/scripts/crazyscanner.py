#!/bin/env python

"""
crazyscan

Continously move a motor randomly between two values

Usage:
   crazyscan.py  <motorpv> <low> <high> <crazyiness> [<zero> <morepos>]
   crazyscan.py  -h | --help

Options:
    <motorpv>        PV of motor 
    <low>            Lower range of motor value
    <high>           Upper range of motor value
    <crazyiness>     Level of 'crazyiness'
                        0 - Not random, just sweeps between low and high 
                        1 - Move randomly between low and high
                        2 - Move randomly between low and high,
                            But 1 in every morepos are between low and zero
    <zero>           Position for time-0                            
    <morepos>        Define how often to spend between zero and high
   
    -h, --help       Print this file

crazyscan is used to move a motor to random positions between low and
high. The different levels of crazyiness defines how random the
positions are, from crazyiness 0 that is not random, to crazyiness 2
that is biased to positions between zero and high.
"""





# import standard python modules
import logging
import random

# import SXR-PYTHON modules
from sxr_common.epics_ims_motor import epics_ims_motor




# Functions to define different levels of 'crazyiness'
def crazyiness_0(low,high, motor) :
    """
    crazyiness_0
    Move motor from low to high and back again
    """

    while True :
        print "Moving: ",low
        motor.mv(low)
        motor.wait_for_motion()

        print "Moving: ", high
        motor.mv(high)
        motor.wait_for_motion()


def crazyiness_1(low, high, motor) :
    """ 
    crazyiness_1
    Move motor randomly between low and high
    """

    while True :
        position = random.uniform(low,high)
        print "Moving: ",position

        motor.mv(position)
        motor.wait_for_motion()


def crazyiness_2(low, high, motor, zero, morepos) :
    """
    crazyiness_2
    Move motor between low and high, but spend more time between zero
    and high relative to low and zero. Continues until "q" is pressed    
    """
    
    while True :
        # Move motor to random position between low and zero
        low_pos = random.uniform(low,zero)
        print "Moving:",low_pos
        motor.mv(low_pos)
        motor.wait_for_motion()

        # Now move motor to random position between zero and high,
        # morepos times
        for i in range(morepos) :
            high_pos = random.uniform(zero,high)            
            print "Moving:",high_pos

            motor.mv(high_pos)
            motor.wait_for_motion()

        


if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
    
    # Read in command line arguments
    import argparse
    parser = \
      argparse.ArgumentParser(description="Continously move a motor \
                                           randomly between two values")
    parser.add_argument('--motorpvname',dest="motorpv",required=True,
                        help="Motor PV")
    parser.add_argument('--from',dest='low',type=float,required=True,
                        help="lower scan value")
    parser.add_argument('--to',dest='high',type=float,required=True,
                        help="upper scan value")
    parser.add_argument('--crazy',dest='crazy',type=int,required=True,
                        help="craziness value")
    parser.add_argument('--zero',dest='zero',type=float,
                        help="zero value for crazyiness 2")
    parser.add_argument('--morepos',dest='morepos',type=int,
                        help="Goes more often to positive values")
    options = parser.parse_args()


    motorpv = options.motorpvname
    low = options.low
    high = options.high
    crazyiness = options.crazy        
    zero = options.zero
    morepos = options.morepos

    # Argument check for crazyiness 2:
    #   - zero and morepos must be defined
    import sys

    if (crazyiness==2) :
        # Check zero was defined
        if zero is None :
            print "zero has to be defined for crazyiness 2"
            sys.exit()
            
        # Check morepos was defined
        if morepos is None :
            print "morepos has to be defined for crazyiness 2"
            sys.exit()


        # Check zero is between low and high
        if (zero > high) or (zero < low) :
            print "zero must be between low(",low,")and high(",high,")"
            sys.exit()

        # Check morepos was defined
        if morepos is None :
            print "morepos must be defined for crazyiness 2"
            sys.exit()

            

    # Connect to motor
    motor = epics_ims_motor(motorpv)

    print "Starting crazyscan"
    try:
        if (crazyiness == 0) :  crazyscan_0(low,high,motor) 
        if (crazyiness == 1) :  crazyscan_1(low,high,motor) 
        if (crazyiness == 2) :  crazyscan_2(low,high,motor, zero, morepos) 
    except KeyboardInterrupt:
        print "Stopping Crazyscan"


