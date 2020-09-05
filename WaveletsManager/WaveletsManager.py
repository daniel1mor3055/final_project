import matplotlib.pyplot as plt
import numpy as np
from pywt import (
    wavedec,
    waverec,
    wavelist,
)

from WaveletsManager.wavelets_manager_constats import (
    SIGNAL_EXTENSIONS,
    CSS_COLORS
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
    def reconstruct(coefficients, wavelets_family, signal_extension):
        return waverec(coeffs=coefficients, wavelet=wavelets_family, mode=signal_extension)

    @staticmethod
    def plot_decompose_summary(signal, coefficients, decompose_level, wavelets_family, signal_extension, save_name=None,
                               show=True):
        length = len(signal)
        reconstructed_signal = WaveletsManager.reconstruct(coefficients, wavelets_family, signal_extension)[:length]

        x_values = np.arange(length)
        num_plots = decompose_level + 3

        plt.figure(figsize=(30, 20))
        # plt.style.use('dark_background')

        # 3 here is because we also with to plot cA,Original Signal, Reconstructed Signal
        plt.subplot(num_plots, 1, 1)
        plt.plot(x_values, signal, color=CSS_COLORS[0])
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.title('Original Signal')

        plt.subplot(num_plots, 1, 2)
        plt.plot(coefficients[0], color=CSS_COLORS[1])
        plt.xlabel('Samples')
        plt.ylabel('cA')
        # plt.title('Approximation Coeff. (cA)')

        for i in range(2, decompose_level + 2):
            plt.subplot(num_plots, 1, i + 1)
            plt.plot(coefficients[i - 1], color=CSS_COLORS[i % len(CSS_COLORS)])
            plt.xlabel('Samples')
            plt.ylabel(f'cD - level {decompose_level - (i - 2)}')
            # plt.title('Detailed Coeff. (cD)')

        plt.subplot(num_plots, 1, num_plots)
        plt.plot(x_values, reconstructed_signal, color=CSS_COLORS[(i + 1) % len(CSS_COLORS)])
        plt.xlabel('Samples')
        plt.ylabel('Amplitude')
        plt.title('Reconstructed Signal')
        if not save_name:
            plt.savefig('summary.png')
        else:
            plt.savefig(f'{save_name}.png')
        if show:
            plt.show()
        else:
            plt.close()
