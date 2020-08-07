from MultiSignal.multi_signal_exceptions import AmplitudesFrequenciesMatchError
from Signal.Signal import Signal


class MultiSignal:
    def __init__(self):
        self.signals = []

    @classmethod
    def from_signals(cls, signals):
        multi_signals = cls()

        multi_signals.signals = signals
        return multi_signals

    @classmethod
    def from_params_lists(cls, amplitudes, frequencies):
        if len(amplitudes) != len(frequencies):
            raise AmplitudesFrequenciesMatchError

        multi_signals = cls()
        for i in range(len(amplitudes)):
            multi_signals.add_signal(amplitudes[i], frequencies[i])

        return multi_signals

    def add_signal(self, amplitude, frequency):
        signal_to_add = Signal(amplitude, frequency)
        self.signals.append(signal_to_add)

    def evaluate(self, duration, samples_per_second):
        evaluated_signal = None
        for signal in self.signals:
            if evaluated_signal is None:
                evaluated_signal = signal.evaluate(duration, samples_per_second)
            else:
                evaluated_signal += signal.evaluate(duration, samples_per_second)

        return evaluated_signal

    def __str__(self):
        signals_repr = '\n'.join(
            [str(index + 1) + ' ' + '\n'.join(signal.__str__().split('\n')[1:]) for index, signal in
             enumerate(self.signals)])
        return 'MultiSignal is composed of the following signals:\n' + \
               f"{signals_repr}"
