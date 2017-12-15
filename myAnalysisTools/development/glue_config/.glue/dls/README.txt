

to do list


#################################
#####Done with new features. Now adding user safety limit wrappers
1) (check) stream lined way to have plot layer activate changes (ok, one new feature).
	a) is the threaded approach safe? use qthread instead?
	b) needs set daemon.
2) more safety on text fields
	a) out of bounds safety on binned statistic.  It's now safe.
3) initial values for binning
4) clean up
	1) get rid of testing/debug text
	2) put user choosable"att"
5) record screen shots and user instructions
6) can it handle deleted subsets?
7) send pull request
	1) prepare test data
	2) how to instructions
8) start user testing


#################################
#######

#################################
#############BUG LIST############
1) (check) fixed. bad binning breaks glue.



1) getting it to working demo mode for scientists
	1) (check) choosing what to plot without changing code.  dig into the API 
	2) implement wiener filtering
	3) (on deck) optimized back end for fast re-calculating of large statistics.  Avoid recalculating mean, slope, etc from scratch...  efficient caching method?
	4) (check) modulation spectroscopy approach.  Is this a beneficial approach?
	5) (check) offsetting
		(a) is still cludgy. using arbitrary indeces that break. would be nice if could 
		(b) apply statistic to specific sub modules?  What about comparing different statistics for single ROI selection?
	6) (check) conditional recalculating statistics. only recalculates when new region selected.
	7) (check) add do recalculation button now
	7) stripped down 2d scatter viewer for faster rendering

2) (check) robust statistics instead of mean,median, slope, etc... also, slope is probably corrupted by brute median truncation.
	a) (check) median truncation.
	b) still need to add robust slope estimator (Theil-Sen or RANSAC)

3) scikit.beam binned_statistic is more efficient. is that compatible with the vectorized version?

5) demo psana shared memory compatibility

6) using psmon visualization (dd's stuff)

7) (check) rapid testing script instead of openining full glue viewer every time. file is called quick debug and is in the sxri0414 smallhdf5 directory
	a) doesn't work for custom viewers

8) (check) built in histogram viewer duplicated and demoed changing some functionality. copied entire histogram viewer from /anaconda/lib/python3.6/site-packages/glue/viewers/histogram to ~/.glue/histogram_mod and added a soft link in /anaconda/lib/python3.6/site-packages/glue/viewers/histogram/layer_artist_mod.py -> /home/sioan/.glue/histogram_mod/layer_artist.py to point. need to change a number of lines of code and the __init__.py. 

9) (check) custom_viewer object access through glue ipython terminal. originally just printed and ctrl-c address and used ctypes to cast object as custom_viewer.

10) (check) zmq can send address of object (maybe use __init__ instead of setup? ) to ipython terminal. no can make qt interaction.

11) (check) maybe see if zmq can directly send pyobject. is this even useful?

12) (check) using gc.get_object() and searching for specific class type to find memory to ctype cast.


13) features
	1) copy and or saving data widget. mask would need to be gotten separately unless hub is used.
	2) (check) assign identifier based on subset, not on memory address
	3) (check) ipython ctyped cast is semi responsive. why the lag? different threads?
		a) because of the redraw. needed to turn off first. 

14) (check) got underlying state (binning and median truncation) to be selective.  

15) (check) reloading parameters from previous subset is proving challenging.  need to test if functionality is even possible

16) add averaging type to state. more difficult than anticipated since it's widget doesn't write to itself



