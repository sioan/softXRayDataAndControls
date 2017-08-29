"""
Mono Auto Focus
Abstract Base class that defines interface for tuning and optimizing
the SXR MONOCHROMATOR focus.

As abstract base class, most methods will be empty and do
nothing. Classes that inherit from monon_autofocus are expected to
have concrete implementations of most methods.
"""

import numpy as np
import matplotlib.pyplot as plt
import logging
import datetime
from common.pypsElog import pypsElog as elog
import tempfile
import shutil
import time


class Mono_Auto_Focus : 
    """
    Abstract base class to optimize the SXR monochromator focus
    Classes that inherit from mono_auto_focus should implement:
    - fit_focus_quality_vs_mirror()
       - returns tuple of best-mirror-position and best-grating-position

   - grating_position(mirror_position)
      - returns grating position using mirror_position
    
    - move_mirror_grating(mirror_pos, grating_pos)
       - Moves mirror and grating to mirror_pos and grating_pos, respectively

    - measure_focus_quality()
       - returns focus_quality

    """

    def __init__(self) :
        """
        Intialize parameters required for scan
        """

        # Set up logger
        self.__logger = logging.getLogger(__name__)

        # Set up variables that define scan range from
        # 'scan_start_pos' to 'scan_stop_pos' in steps of 'scan_delta' 
        self.scan_start_pos = None
        self.scan_stop_pos = None
        self.scan_delta = None
        
        # Variables to log mirror, grating, and focus-quality during
        # auto-focus optimization
        self.mirror_pos_log = None
        self.grating_pos_log = None
        self.focus_quality_log = None

        # Optimal mirror,grating position
        self.best_mirror_pos = None
        self.best_grating_pos = None

        # Focus vs mirror-position plot variable
        self.fig = None
        self.ax = None

        # String of scan results
        self.__scanresult_string = None


    def find_best_focus(self) :
        """
        Main function that steps through the process of finding the
        best mirror foccus position of the SXR monochromator

        All the methods, except run_mirror_scan are empty. They are
        expected to be defined in the classes that inherit from
        mono_autofocus. 
        """        

        self.__logger.info("Find best mirror focus")

        # Scan mirror position
        self.run_mirror_scan()

        # Fit mirror position vs focus-quality to find optimum 
        self.fit_focus_quality_vs_mirror()

        # Print results of scan and fit to screen
        self.print_results()

        # Move to new mirror,grating position
        new_positions_accepted = self.move_to_optimal_positions()

        # Print results to screen, post to elog, and log results if
        # mirror, grating were moved
        if new_positions_accepted :
            self.post_results()
            self.log_results()

        return

        
                
    def run_mirror_scan(self) :
        """
        Scan through mirror positions, adjusting grating to keep
        spectrum centered.  At each position measure focus quality. 

        All data are logged 
        """
        
        self.__logger.info("Running mirror scan")
        time_start = datetime.datetime.now()

        # Scan mirror from 'scan_start_pos' to 'scan_stop_pos' in
        # steps of 'scan_delta'
        self.mirror_pos_log = np.arange(self.scan_start_pos,
                                        self.scan_stop_pos,
                                        self.scan_delta)
        
        # set up logs for grating position and focus quality
        self.grating_pos_log = []
        self.focus_quality_log = []

        # Initialize plot of mirror_pos vs focus_quality
        plt.ion()
        self.fig = plt.figure("Focus Vs Mirror")
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.ax.set_ylabel("Focus")
        self.ax.set_xlabel("Mirror Position / mm")
        focus_plot = np.zeros(len(self.mirror_pos_log))
        line1, = self.ax.plot(self.mirror_pos_log,
                              focus_plot,
                              'r-',marker='o')
        self.fig.canvas.draw()


        for index,mirror_pos in enumerate(self.mirror_pos_log) :

            # Calculate new grating position
            grating_pos = self.grating_position(mirror_pos)

            # Move mirror and grating
            self.move_mirror_grating(mirror_pos, grating_pos)

            # CRUCIAL: Wait 1 second for mechanics to stabilize before
            # taking image 
            time.sleep(1)
            
            # Measure focus quality
            focus_quality = self.measure_focus_quality()

            # Update grating position and focus quality logs
            self.grating_pos_log.append(grating_pos)
            self.focus_quality_log.append(focus_quality)
            
            focus_plot[index] = focus_quality
            self.ax.set_ylim((0.8*np.min(focus_plot)),
                             (1.2*np.max(focus_plot)))
            line1.set_ydata(focus_plot)
            self.fig.canvas.draw()
            
        time_end = datetime.datetime.now()
        time_diff = time_end - time_start
        self.__logger.info("Mirror scan finished (time taken: %s)"%time_diff)

        return
            
      
    
    def move_to_optimal_positions(self) :
        """
        Move mirror,grating to optimal position, if desired 
        """

        response = \
            raw_input("Move MONO to optimal position? [press 'Y' to accept] ")

        if (response.lower() == 'y') :
            self.__logger.info("Moving MONO to optimal position")
            self.move_mirror_grating(self.best_mirror_pos,self.best_grating_pos)
            return True
        else :
            self.__logger.info("Selected NOT to move MONO")
            return False



    def print_results(self) :
        """
        Print data & results of the scan to screen        
        """
        self.__logger.info("Update plots")
        self.ax.vlines(self.best_mirror_pos,
                       *self.ax.get_ylim(),
                       color="red")
        self.fig.canvas.draw()
            

        self.__logger.info("Print results to screen")


        tableString =  "Mirror \t Grating \t Focus Quality \n"
        tableString += "------ \t ------- \t --------- \n"
    
        for line in range(self.mirror_pos_log.size):
            tableString += "%5.3f \t %5.3f \t %5.3f\n"%(self.mirror_pos_log[line],
                                                        self.grating_pos_log[line],
                                                        self.focus_quality_log[line])
                
        tableString += "\n"
        tableString += "Optimal Mirror Position: %0.3f \n"%(self.best_mirror_pos)
        tableString += "Optimal Grating Position: %0.3f \n"%(self.best_grating_pos)

        print tableString

        self.__scanresult_string = tableString
         
        return


    def post_results(self) :
        """
        Post data & results to elog
        """

        self.__logger.info("Post results to elog")

        # Save scan plot in a temporary area
        tempDirName = tempfile.mkdtemp()        
        pltfilename = tempDirName + "/mono_scan_results.png"
        self.__logger.debug("Writing plots to %s"%pltfilename)
        self.fig.savefig(pltfilename)

        # Post results and plot to elog
        self.__logger.debug("Sending results to elog")
        sxrelog = elog()
        sxrelog.submit(text=self.__scanresult_string,
                       tag="MONO autofocus",tag2="sxrpython",
                       file=pltfilename,
                       file_descr="Mono Autotune Scan")

        # Clean up temp area
        self.__logger.debug("Cleaing  up temp area")
        shutil.rmtree(tempDirName)


        return

    def log_results(self) :
        """
        Write data and results of scan to log-file for post-analysis 
        """

        self.__logger.info("Write results to log file")
        self.__logger.critical("Not implemented yet")
    
        return

        
###################################
# FUNCTIONS TO BE OVER-WRITTEN 
###################################

    def grating_position(self, mirror_pos) :
        """
        Calculate position to move grating position to keep spectrum
        centered as a function to mirror_pos.

        Input: mirror_pos => mirror position
        Return: grating position
        """

        self.__logger.info("Calculate new grating position")
        self.__logger.critical("Not implemented")
        return 0.0


    def move_mirror_grating(self, mirror_pos, grating_pos) :
        """
        Move the mirror and grating to mirror_pos and grating_pos, respectively.

        Input: mirror_pos => mirror position
               grating_pos => grating position
        Return: Nothing
        """

        self.__logger.info("Move mirror and grating")
        self.__logger.critical("Not implemented")
        return

    
    def measure_focus_quality(self) :
        """
        Measure quality of focus
        
        Return : number that quantifies focus quality. 
        """

        self.__logger.info("Measure focus quality")
        self.__logger.critical("Not implemented")
        return 0.0


    def fit_focus_quality_vs_mirror(self) :
        """        
        Uses data in mirror_pos_log and focus_quality_log to find best
        focus. 
        self.__grating_pos_log is availalbe if needed.

        Optimal positions are written to best_mirror_pos and best_grating_pos

        Return: None
        """

        self.__logger.info("Fit focus_quality vs mirror_position")
        self.__logger.critical("Not implemented")

        self.best_mirror_pos = 0.0
        self.best_grating_pos = 0.0

        return

    





##############################
#  Test code

if __name__ == "__main__" :
#    logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    
    mono_auto_focus = Mono_Auto_Focus()
    mono_auto_focus.scan_start_pos = -10.0
    mono_auto_focus.scan_stop_pos = 10.0
    mono_auto_focus.scan_delta = 1.0

    mono_auto_focus.find_best_focus()

    



    
