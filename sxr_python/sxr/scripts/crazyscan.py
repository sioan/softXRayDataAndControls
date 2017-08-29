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


# Standard PYTHON random number generator
import random

# SXD Python modules
from common.motor import Motor as psmotor



def crazyscan_0(low,high, epicsMotor) :
    """
    Move motor from low to high and back again
    """

    while True :
        print "Moving: ",low
        epicsMotor.move(low)
        epicsMotor.wait()
        print "Moving: ", high
        epicsMotor.move(high)
        epicsMotor.wait()

        

def crazyscan_1(low, high, epicsMotor) :
    """ 
   Move motor randomly between low and high
    """

    while True :
        position = random.uniform(low,high)
        print "Moving: ",position

        epicsMotor.move(position)
        epicsMotor.wait()

        

def crazyscan_2(low, high, epicsMotor, zero, morepos) :
    """
    Move motor between low and high, but spend more time between zero
    and high relative to low and zero. Continues until "q" is pressed    
    """
    
    while True :
        # Move motor to random position between low and zero
        low_pos = random.uniform(low,zero)
        print "Moving:",low_pos
        epicsMotor.move(low_pos)
        epicsMotor.wait()

        # Now move motor to random position between zero and high,
        # morepos times
        for i in range(morepos) :
            high_pos = random.uniform(zero,high)            
            print "Moving:",high_pos

            epicsMotor.move(high_pos)
            epicsMotor.wait()

        


if __name__ == "__main__" :
    # Read in command line arguments
    from docopt import docopt
    arguments = docopt(__doc__,options_first=True)
    print arguments
    
    motorpv = arguments['<motorpv>']
    low = float(arguments['<low>'])
    high = float(arguments['<high>'])
    crazyiness = int(arguments['<crazyiness>'])
    
    zero = None
    morepos = None

    # Argument check for crazyiness 2:
    #   - zero and morepos must be defined
    import sys

    if (crazyiness==2) :
        # Check zero was defined
        if arguments['<zero>'] is None :
            print "zero has to be defined for crazyiness 2"
            sys.exit()
            
        # Check morepos was defined
        if arguments['<morepos>'] is None :
            print "morepos has to be defined for crazyiness 2"
            sys.exit()


        # Convert zero and morepos
        zero = float(arguments['<zero>'])
        morepos = int(arguments['<morepos>'])

        # Check zero is between low and high
        if (zero > high) or (zero < low) :
            print "zero must be between low(",low,")and high(",high,")"
            sys.exit()

        # Check morepos was defined
        if morepos is None :
            print "morepos must be defined for crazyiness 2"
            sys.exit()

            

    # Connect to motor
    epicsMotor = psmotor(motorpv)

    print "Starting crazyscan"
    try:
        if (crazyiness == 0) :  crazyscan_0(low,high,epicsMotor) 
        if (crazyiness == 1) :  crazyscan_1(low,high,epicsMotor) 
        if (crazyiness == 2) :  crazyscan_2(low,high,epicsMotor, zero, morepos) 
    except KeyboardInterrupt:
        print "Stopping Crazyscan"



