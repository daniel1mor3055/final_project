import matplotlib.pyplot as plt
import numpy as np
from pywt import (
    wavedec,
    waverec,
    families,
)

from WaveletsManager.wavelets_manager_constats import SIGNAL_EXTENSIONS, WAVELET_FAMILIES, CSS_COLORS
from WaveletsManager.wavelets_manager_exceptions import ReconstructionError, SignalExtensionError, WaveletFamilyError


class WaveletsManager:
    def __init__(self, signal):
        self.signal = signal
        self.plot_coefficients = None
        self.wavelets_family = None
        self.signal_extension = None
        self.decompose_level = None
        self._reconstructed_signal = None

    def decompose(self, signal_extension='symmetric', wavelets_family='haar', decompose_level=3):
        self.signal_extension, self.wavelets_family, self.decompose_level = signal_extension, wavelets_family, decompose_level
        if signal_extension not in SIGNAL_EXTENSIONS:
            raise SignalExtensionError

        if wavelets_family not in WAVELET_FAMILIES:
            raise WaveletFamilyError

        coefficients = wavedec(data=self.signal, wavelet=wavelets_family, mode=signal_extension, level=decompose_level)
        self.coefficients = coefficients.copy()
        return coefficients

    def reconstruct(self):
        required_properties = [self.coefficients, self.wavelets_family, self.signal_extension]
        if all(required_properties):
            reconstructed_signal = waverec(coeffs=self.coefficients, wavelet=self.wavelets_family,
                                           mode=self.signal_extension)
            self._reconstructed_signal = reconstructed_signal.copy()
            return reconstructed_signal
        else:
            raise ReconstructionError(required_properties)

    @staticmethod
    def get_available_families():
        return families()

    def plot_summary(self):
        if not self._reconstructed_signal:
            self.reconstruct()

        length = len(self.signal)
        reconstructed_signal = self._reconstructed_signal[:length]

        x_values = np.arange(length)
        num_plots = self.decompose_level + 3

        plt.figure(figsize=(30, 20))

        # 3 here is because we also with to plot cA,Original Signal, Reconstructed Signal
        plt.subplot(num_plots, 1, 1)
        plt.plot(x_values, self.signal, color=CSS_COLORS[0])
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.title('Original Signal')

        plt.subplot(num_plots, 1, 2)
        plt.plot(self.coefficients[0], color=CSS_COLORS[1])
        plt.xlabel('Samples')
        plt.ylabel('cA')
        # plt.title('Approximation Coeff. (cA)')

        for i in range(2, self.decompose_level + 2):
            plt.subplot(num_plots, 1, i + 1)
            plt.plot(self.coefficients[i - 1], color=CSS_COLORS[i % len(CSS_COLORS)])
            plt.xlabel('Samples')
            plt.ylabel(f'cD - level {self.decompose_level - (i - 2)}')
            # plt.title('Detailed Coeff. (cD)')

        plt.subplot(num_plots, 1, num_plots)
        plt.plot(x_values, reconstructed_signal, color=CSS_COLORS[(i + 1) % len(CSS_COLORS)])
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.title('Reconstructed Signal')
        plt.show()

    def plot_coefficients(self):
        raise NotImplementedError
