source /reg/g/pcds/setup/pyca.sh

#export DAQREL=/reg/neh/home/weaver/current
#export DAQREL=/reg/neh/home/tomytsai/project/daqPrinceton
export DAQREL=/reg/g/pcds/dist/pds/sxr/current
export AMIREL=/reg/g/pcds/dist/pds/sxr/ami-current
export PYTHONPATH=${DAQREL}/build/pdsapp/lib/x86_64-linux-opt:${AMIREL}/build/ami/lib/x86_64-linux-opt:${PYTHONPATH}
export LD_LIBRARY_PATH=${DAQREL}/build/pdsdata/lib/x86_64-linux-opt:${DAQREL}/build/pdsapp/lib/x86_64-linux-opt:${DAQREL}/build/pds/lib/x86_64-linux-opt:/reg/g/pcds/package/qt-4.3.4_x86_64/lib:${LD_LIBRARY_PATH}

#export LD_LIBRARY_PATH="/reg/neh/home/tomytsai/project/daqPrinceton/build/pdsapp/lib/x86_64-linux-opt:/reg/neh/home/tomytsai/project/daqPrinceton/build/pdsdata/lib/x86_64-linux-opt:${LD_LIBRARY_PATH}"
