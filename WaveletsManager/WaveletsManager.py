from pywt import (
    wavedec,
    waverec,
    wavelist,
)

from WaveletsManager.wavelets_manager_constats import (
    SIGNAL_EXTENSIONS
)
from WaveletsManager.wavelets_manager_exceptions import (
    SignalExtensionError,
    WaveletFamilyError
)


class WaveletsManager:
    @staticmethod
    def decompose(signal, signal_extension='symmetric', wavelets_family='haar', decompose_level=3):
        if signal_extension not in SIGNAL_EXTENSIONS:
            raise SignalExtensionError

        if wavelets_family not in wavelist():
            raise WaveletFamilyError(wavelist())

        coefficients = wavedec(data=signal, wavelet=wavelets_family, mode=signal_extension, level=decompose_level)
        return coefficients

    @staticmethod
    def reconstruct(coefficients, wavelets_family, signal_extension='symmetric'):
        return waverec(coeffs=coefficients, wavelet=wavelets_family, mode=signal_extension)
