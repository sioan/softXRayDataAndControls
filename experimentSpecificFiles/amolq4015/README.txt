hummingbird directory is the local working copy.
can be pulled from github.com/fxihub/hummingbird.git

configuration is the location of the configuration files.

./hummingbird.py -h
-b is back end (stuff that runs on mon nodes) this is the config file.


-i is stuff that runs on psusr (i.e. the gui). completely separate program
-p for specifiying port (13131 works on psana)
-no-restore flag prevents loading previous configurations


lots of configuration files in configuration. Just use conf.py

conf.py loads conf_amolq4015.py
