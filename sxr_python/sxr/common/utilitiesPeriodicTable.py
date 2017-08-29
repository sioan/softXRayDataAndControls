import numpy
from periodictable.xsf import xray_wavelength, index_of_refraction
from periodictable.util import require_keywords

@require_keywords
def attenuation_length(compound, density=None, natural_density=None,
                       energy=None, wavelength=None):
    """
    Calculates the attenuation length for a compound
                Transmisison if then exp(-thickness/attenuation_length)

    :Parameters:
        *compound* : Formula initializer
            Chemical formula.
        *density* : float | |g/cm^3|
            Mass density of the compound, or None for default.
        *natural_density* : float | |g/cm^3|
            Mass density of the compound at naturally occurring isotope abundance.
        *wavelength* : float or vector | |Ang|
            Wavelength of the X-ray.
        *energy* : float or vector | keV
            Energy of the X-ray, if *wavelength* is not specified.

    :Returns:
        *attenuation_length* : vector | |m|
            as function of (energy)

    :Notes:

    against http://henke.lbl.gov/optical_constants/
    """
    if energy is not None: wavelength = xray_wavelength(energy)
    assert wavelength is not None, "scattering calculation needs energy or wavelength"
    if (numpy.isscalar(wavelength)): wavelength=numpy.array( [wavelength] )
    n = index_of_refraction(compound=compound,
                            density=density, natural_density=natural_density,
                            wavelength=wavelength)
    attenuation_length = (wavelength*1e-10)/ (4*numpy.pi*numpy.imag(n))
    return numpy.abs(attenuation_length)
