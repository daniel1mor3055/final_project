import numpy as np

from global_constants import SAMPLES_PER_SECOND


class Transient:
    def __init__(self, indices):
        self.indices = indices

    def __str__(self):
        return f'Transient occurred in the following indices:\n{self.indices}\n'


class FailTransient(Transient):
    def __init__(self, indices, time_domain_samples):
        super().__init__(indices)
        self.time_domain_samples = time_domain_samples

    def get_rms(self):
        return np.sqrt(np.mean(np.square(np.array(self.time_domain_samples))))

    def get_energy(self):
        return np.sum(np.square(np.array(self.time_domain_samples)))

    def get_max_amplitude(self):
        return np.max(np.abs(np.array(self.time_domain_samples)))

    def get_duration(self):
        return (self.indices[1] - self.indices[0]) / SAMPLES_PER_SECOND

    def __str__(self):
        return super().__str__() + 'Type = Fail Transient\n' + \
               f'RMS = {self.get_rms()}\n' + \
               f'Energy = {self.get_energy()}\n' + \
               f'Max Amplitude = {self.get_max_amplitude()}\n' + \
               f'Duration = {self.get_duration()} seconds\n'


class LoadTransient(Transient):
    def __init__(self, indices):
        super().__init__(indices)

    def __str__(self):
        return super().__str__() + 'Type = Load Transient\n'
