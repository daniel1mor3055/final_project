from pywt import (
    wavedec,
    waverec,
    families,
)
import matplotlib.pyplot as plt
import numpy as np

from WaveletsManager.wavelets_manager_constats import SIGNAL_EXTENSIONS, WAVELET_FAMILIES
from WaveletsManager.wavelets_manager_exceptions import ReconstructionError, SignalExtensionError, WaveletFamilyError


class WaveletsManager:
    def __init__(self, signal):
        self.signal = signal
        self.plot_coefficients = None
        self.wavelets_family = None
        self.signal_extension = None
        self.decompose_level = None

    def decompose(self, signal_extension='sym', wavelets_family='haar', decompose_level=3):
        self.signal_extension, self.wavelets_family, self.decompose_level = signal_extension, wavelets_family, decompose_level
        if signal_extension not in SIGNAL_EXTENSIONS:
            raise SignalExtensionError

        if wavelets_family not in WAVELET_FAMILIES:
            raise WaveletFamilyError

        coefficients = wavedec(data=self.signal, wavelet=wavelets_family, mode=signal_extension, level=decompose_level)
        self.plot_coefficients = coefficients.copy()
        return coefficients

    def reconstruct(self):
        required_properties = [self.plot_coefficients, self.wavelets_family, self.signal_extension]
        if all(required_properties):
            reconstructed_signal = waverec(coeffs=self.plot_coefficients, wavelet=self.wavelets_family,
                                           mode=self.signal_extension)
            return reconstructed_signal
        else:
            raise ReconstructionError(required_properties)

    @staticmethod
    def get_available_families():
        return families()

    def plot_summary(self):
        raise NotImplementedError

    def plot_coefficients(self):
        raise NotImplementedError
