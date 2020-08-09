import matplotlib.pyplot as plt


class SignalPlotter:
    def __init__(self):
        pass

    @staticmethod
    def plot_signal(signal_to_plot, save_name, title='Sample Title', show=True):
        plt.plot([i for i in range(len(signal_to_plot))], signal_to_plot)
        plt.title(title)
        plt.savefig(save_name + '.png')
        if show:
            plt.show()
        else:
            plt.close()
