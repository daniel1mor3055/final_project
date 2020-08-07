import matplotlib.pyplot as plt


class SignalPlotter:
    def __init__(self):
        pass

    @staticmethod
    def plot_signal(signal_to_plot, title, show=True):
        plt.plot([i for i in range(len(signal_to_plot))], signal_to_plot)
        plt.plot([i for i in range(len(signal_to_plot))], signal_to_plot)
        plt.title(title)
        if show:
            plt.show()
