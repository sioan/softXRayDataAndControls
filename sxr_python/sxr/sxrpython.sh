#! /bin/bash

SETUPDIR=`dirname "$0"`
source ${SETUPDIR}/sxrenv.sh

ipython --no-banner --no-confirm-exit --profile sxr-daq -i -c "%run ${SETUPDIR}/sxrload.py"
