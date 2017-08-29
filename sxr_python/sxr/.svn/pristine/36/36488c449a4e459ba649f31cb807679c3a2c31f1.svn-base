source /reg/g/pcds/setup/pathmunge.sh

#ldpathmunge /reg/g/psdm/sw/external/boost/1.49.0-python2.7/x86_64-rhel6-gcc44-opt/lib
#ldpathmunge /reg/g/psdm/sw/releases/ana-current/arch/x86_64-rhel5-gcc41-opt/lib

#pythonpathmunge /reg/g/psdm/sw/releases/ana-current/arch/x86_64-rhel5-gcc41-opt/python

#pythonpathmunge /reg/g/psdm/sw/releases/ana-current/arch/x86_64-rhel5-gcc41-opt/python/pyextra


export EPICS_CA_MAX_ARRAY_BYTES=8000000
export PSPKG_ROOT=/reg/common/package

export PSPKG_RELEASE="sxr-1.1.0"

source $PSPKG_ROOT/etc/set_env.sh

# Add script's directory to PYTHON path
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd && echo x)"
SCRIPTDIR="${SCRIPTDIR%x}"
pythonpathmunge $SCRIPTDIR


# Add environment variables required for motor auto-config
export DEVICE_CONFIG_TEMPLATE_DIR=/reg/neh/operator/sxropr/device_config/ims_templates
export DEVICE_CONFIG_TEMPLATE_DEFAULT=sxd_ims_config.tmp
export DEVICE_CONFIG_DIR=/reg/neh/operator/sxropr/device_config/ims
pathmunge /reg/neh/operator/sxropr/device_config



#pythonpathmunge ~mitra/Work/pypsalg/arch/x86_64-rhel5-gcc41-opt/python
