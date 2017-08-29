#!/bin/bash

# Change to directory containing the script
homepath=`dirname $0`
cd $homepath

# Setup edm environment
PACKAGE_TOP=/reg/g/pcds/package
export EPICS_SITE_TOP=$PACKAGE_TOP/epics/3.14
export EPICS_HOST_ARCH=$($EPICS_SITE_TOP/base/current/startup/EpicsHostArch.pl)

export EDMFILES=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMFILTERS=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMHELPFILES=$EPICS_SITE_TOP/extensions/current/helpFiles
export EDMLIBS=$EPICS_SITE_TOP/extensions/current/lib/$EPICS_HOST_ARCH
export EDMOBJECTS=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMPVOBJECTS=$EPICS_SITE_TOP/extensions/current/templates/edm
export EDMUSERLIB=$EPICS_SITE_TOP/extensions/current/lib/$EPICS_HOST_ARCH
export EDMACTIONS=$PACKAGE_TOP/tools/edm/config

export EDMDATAFILES=.:..

# Support for slow cams
export EPICS_CA_MAX_ARRAY_BYTES=8000000

pathmunge ()
{
        if [ ! -d $1 ] ; then
                return
        fi
        if ! echo $PATH | /bin/egrep -q "(^|:)$1($|:)" ; then
                if [ "$2" = "after" ] ; then
                        PATH=$PATH:$1
                else
                        PATH=$1:$PATH
                fi
        fi
}

pathmunge $EPICS_SITE_TOP/base/current/bin/$EPICS_HOST_ARCH after
pathmunge $EPICS_SITE_TOP/extensions/current/bin/$EPICS_HOST_ARCH after
unset pathmunge


edm -x -eolc -m "MOTOR=$1" pp_gui.edl &
/reg/g/pcds/package/epics/3.14/modules/pcds_motion/R2.3.5/launch-motor.sh $1 
/reg/g/pcds/package/epics/3.14/modules/pcds_motion/R2.3.5/launch-motor.sh $2
/reg/g/pcds/package/epics/3.14/modules/pcds_motion/R2.3.5/launch-motor.sh $3
