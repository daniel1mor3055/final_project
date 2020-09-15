import matplotlib.pyplot as plt
import numpy as np

from Transient.Transient import FailTransient
from WaveletsManager.WaveletsManager import WaveletsManager
from WaveletsManager.wavelets_manager_constats import CSS_COLORS
from global_constants import TRIAL_NAME


class SignalPlotter:
    def __init__(self):
        pass

    @staticmethod
    def plot_signal(signal_to_plot, save_name, linewidth=None, color=None, title='Sample Title', show=True):
        plt.figure(figsize=(100, 20))
        # plt.style.use('dark_background')
        plt.plot([i for i in range(len(signal_to_plot))], signal_to_plot, color=color, linewidth=linewidth)
        plt.title(title)
        plt.savefig(f'{save_name}.png')
        if show:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def plot_dft_domain(dft, save_name, title='Dft Title', show=True):
        plt.plot(np.linspace(-np.pi, np.pi, len(dft)), dft)
        plt.title(title)
        plt.savefig(f'{save_name}.png')
        if show:
            plt.show()
        else:
            plt.close()

    @staticmethod
    def _get_ticks_for_x_axis(transients):
        starts_ends = []
        for transient in transients:
            starts_ends += [transient.indices[0], transient.indices[1]]

        ticks = []
        for transient in transients:
            ticks += ['start\nfail', 'end\nfail'] if isinstance(transient, FailTransient) else ['start\nload',
                                                                                                'end\nload']

        return starts_ends, ticks

    @staticmethod
    def plot_decompose_summary(signal, coefficients, decompose_level, wavelets_family, signal_extension, transients,
                               moving_average, save_name=None, show=True):

        ticks_for_x_axis = SignalPlotter._get_ticks_for_x_axis(transients)

        length = len(signal)
        reconstructed_signal = WaveletsManager.reconstruct(coefficients, wavelets_family, signal_extension)[:length]

        x_values = np.arange(length)
        num_plots = decompose_level + 4

        plt.figure(figsize=(30, 20))

        # 3 here is because we also with to plot cA,Original Signal, Reconstructed Signal
        plt.subplot(num_plots, 1, 1)
        plt.plot(x_values, signal, color=CSS_COLORS[0])
        plt.xticks(ticks_for_x_axis[0], ticks_for_x_axis[1])
        plt.ylabel('Amplitude')
        plt.title(f'{TRIAL_NAME} Original Signal')

        plt.subplot(num_plots, 1, 2)
        plt.plot(coefficients[0], color=CSS_COLORS[1])
        plt.ylabel('cA')
        plt.title(f'{TRIAL_NAME} Approximation Coeff. (cA)')

        for i in range(2, decompose_level + 2):
            plt.subplot(num_plots, 1, i + 1)
            plt.plot(coefficients[i - 1], color=CSS_COLORS[i % len(CSS_COLORS)])
            plt.ylabel(f'cD - level {decompose_level - (i - 2)}')
            plt.title(f'{TRIAL_NAME} Detailed Coeff. (cD)')

        plt.subplot(num_plots, 1, num_plots - 1)
        plt.plot(x_values, reconstructed_signal, color=CSS_COLORS[(i + 1) % len(CSS_COLORS)])
        plt.ylabel('Amplitude')
        plt.title(f'{TRIAL_NAME} Reconstructed Signal')

        plt.subplot(num_plots, 1, num_plots)
        plt.plot(moving_average, color=CSS_COLORS[(i + 2) % len(CSS_COLORS)])
        plt.ylabel('Amplitude')
        plt.title(f'{TRIAL_NAME} Moving Average')

        if not save_name:
            plt.savefig(f'{TRIAL_NAME}_summary.png')
        else:
            plt.savefig(f'{save_name}.png')
        if show:
            plt.show()
        else:
            plt.close()
