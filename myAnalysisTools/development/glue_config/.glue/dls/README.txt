

to do list

brain storm (then order)





1) getting it to working demo mode for scientists
	1) (check) choosing what to plot without changing code.  dig into the API 
	2) implement wiener filtering
	3) (on deck) optimized back end for fast re-calculating of large statistics.  Avoid recalculating mean, slope, etc from scratch...  efficient caching method?
	4) (check) modulation spectroscopy approach.  Is this a beneficial approach?
	5) (check) offsetting
		(a) is still cludgy. using arbitrary indeces that break. would be nice if could 
		(b) apply statistic to specific sub modules?  What about comparing different statistics for single ROI selection?
	6) (check) conditional recalculating statistics. only recalculates when new region selected.
	7) add do recalculation button now
	7) stripped down 2d scatter viewer for faster rendering

2) robust statistics instead of mean,median, slope, etc... also, slope is probably corrupted by brute median truncation.

3) scikit.beam binned_statistic is more efficient. is that compatible with the vectorized version?

5) demo psana shared memory compatibility

6) using psmon visualization (damiani)

7) (check) rapid testing script instead of openining full glue viewer every time. file is called quick debug and is in the sxri0414 smallhdf5 directory
	a) doesn't work for custom viewers

8) (check) got built in histogram viewer duplicated and demoed changing some functionality. copied entire histogram viewer from /anaconda/lib/python3.6/site-packages/glue/viewers/histogram to ~/.glue/histogram_mod and added a soft link in /anaconda/lib/python3.6/site-packages/glue/viewers/histogram/layer_artist_mod.py -> /home/sioan/.glue/histogram_mod/layer_artist.py to point. need to change a number of lines of code and the __init__.py. 

