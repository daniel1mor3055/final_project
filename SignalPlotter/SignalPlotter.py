import matplotlib.pyplot as plt
import numpy as np


class SignalPlotter:
    def __init__(self):
        pass

    @staticmethod
    def plot_signal(signal_to_plot, save_name, linewidth=None, color=None, title='Sample Title', show=True):
        plt.figure(figsize=(100     , 20))
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
