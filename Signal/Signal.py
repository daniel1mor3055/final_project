import numpy as np


class Signal:
    def __init__(self, amplitude, frequency, phase=0):
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase

    def __str__(self):
        return 'Signal is composed of:\n' + \
               'Base params:\n' + \
               f'\tamplitude={self.amplitude}\n' + \
               f'\tfrequency={self.frequency}\n' + \
               f'\tphase={self.phase}\n'

    def evaluate(self, duration, samples_per_second):
        sampling_times = np.array([i / samples_per_second for i in range(duration * samples_per_second)])
        evaluated_signal = self.amplitude * np.sin(2 * np.pi * self.frequency * sampling_times)
        return evaluated_signal
