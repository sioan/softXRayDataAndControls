#!/usr/bin/env bash

unset LD_LIBRARY_PATH
unset PYTHONPATH

export ONDA_INSTALLATION_DIR=/reg/neh/operator/amoopr/experiments/amolq1415/onda-20170713-photofragmentation

source /reg/g/psdm/etc/psconda.sh

export PYTHONPATH=${ONDA_INSTALLATION_DIR}:${ONDA_HIDRA_API_DIR}:${PYTHONPATH}
export PATH=${ONDA_INSTALLATION_DIR}:${ONDA_INSTALLATION_DIR}/GUI/:${ONDA_INSTALLATION_DIR}/tools/:${PATH}
