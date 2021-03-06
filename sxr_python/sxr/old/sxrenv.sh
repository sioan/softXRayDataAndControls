source /reg/g/pcds/setup/pathmunge.sh

PKG_BAS="/reg/common/package/release"
XCS_REL="sxr-0.0.4"
RH5_BLD="x86_64-rhel5-gcc41-opt"
RH6_BLD="x86_64-rhel6-gcc44-opt"
RH5_PTH=$PKG_BAS/$XCS_REL/$RH5_BLD
RH6_PTH=$PKG_BAS/$XCS_REL/$RH6_BLD

if [ "$LSB_FAMILY" == "rhel6" ]; then
  pathmunge       "$RH6_PTH/bin"
  ldpathmunge     "$RH6_PTH/lib"
  pythonpathmunge "$RH6_PTH/python"
elif [ "$LSB_FAMILY" == "rhel5" ]; then
  pathmunge       "$RH5_PTH/bin"
  ldpathmunge     "$RH5_PTH/lib"
  pythonpathmunge "$RH5_PTH/python"
elif [ "$LSB_FAMILY" == "" ]; then
  echo "Cannot determine Linux distribution"
else 
  echo "Linux distribution '$LSB_FAMILY' unsupported by this script"
fi

export EPICS_CA_MAX_ARRAY_BYTES=8000000
