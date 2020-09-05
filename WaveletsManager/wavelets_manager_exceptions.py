from WaveletsManager.wavelets_manager_constats import (
    SIGNAL_EXTENSIONS,
)


class SignalExtensionError(Exception):
    def __init__(self, message='Please provide signal extension from the following options:\n\t'):
        super().__init__(message + '\n\t'.join(SIGNAL_EXTENSIONS))


class WaveletFamilyError(Exception):
    def __init__(self, wavelet_families, message='Please provide wavelet family from the following options:\n\t'):
        super().__init__(message + '\n\t'.join(wavelet_families))
