from SignalGenerator.signal_generator_constants import NUM_OF_DRAWS_AMPLITUDES_OF_DIFF_HARMONICS
from SignalGenerator.signal_generator_exceptions import SampleRateError, MissingPropertiesError
from MultiSignal.MultiSignal import MultiSignal
import numpy as np


class SignalGenerator:
    def __init__(self):
        self.base_amplitude = None
        self.base_frequency = None
        self.num_diff_harmonics = None
        self.noise_params = None
        self.duration = 0
        self.samples_per_second = 0
        self.num_regular_transients = None
        self.num_failure_transients = None
        self._possible_frequencies = None

    def __str__(self):
        missing_properties = self._get_missing_properties()
        missing_properties_repr = 'SignalGenerator still missing the following parameters:\n\t' + \
                                  '\n\t'.join(missing_properties)

        assigned_properties_repr = 'SignalGenerator has the following parameters:\n' + \
                                   f'\tbase frequency={self.base_frequency}\n' + \
                                   f'\tbase amplitude={self.base_amplitude}\n' + \
                                   f'\tnum of different harmonics={self.num_diff_harmonics}\n' + \
                                   f'\tnoise parameters={self.noise_params}\n' + \
                                   f'\tduration={self.duration}\n' + \
                                   f'\tsamples per seconds={self.samples_per_second}\n' + \
                                   f'\tnum of regular transients={self.num_regular_transients}\n' + \
                                   f'\tnum of failure transients={self.num_failure_transients}\n'

        return assigned_properties_repr + (missing_properties_repr if missing_properties else '')

    def generate(self):
        missing_properties = self._get_missing_properties()
        if missing_properties:
            raise MissingPropertiesError(missing_properties)

        lst_of_clean_signals = self._create_clean_signals()
        return lst_of_clean_signals

    def _create_clean_signals(self):
        lst_of_different_signals = list()
        for i in range(self.num_regular_transients + 1):
            amplitudes_of_diff_harmonics = self._extract_amplitudes_with_respect_to_harmonics()

            multi_signal = MultiSignal.from_params_lists(amplitudes_of_diff_harmonics, self._possible_frequencies)
            print(multi_signal)
            # multi_sine_waveform = _multi_sine_waveforms(amplitudes=amplitudes, frequencies=frequencies,
            #                                             duration=duration, samples_per_second=samples_per_second)
            # lst_of_different_signals.append(multi_sine_waveform)

        return lst_of_different_signals

    def _extract_amplitudes_with_respect_to_harmonics(self):
        mean, var = self.noise_params['mean'], self.noise_params['var']
        counts_of_different_harmonics = np.zeros(self.num_diff_harmonics)
        draws = np.abs(np.random.normal(mean, var, size=NUM_OF_DRAWS_AMPLITUDES_OF_DIFF_HARMONICS))
        for draw in draws:
            counts_of_different_harmonics[int(draw / (var / 2))] += 1

        count_of_base_amplitude = counts_of_different_harmonics[0]
        amplitudes_of_diff_harmonics = [count * self.base_amplitude / count_of_base_amplitude for count in
                                        counts_of_different_harmonics]

        return amplitudes_of_diff_harmonics

    def _get_missing_properties(self):
        missing_properties = [attr for attr in dir(self) if
                              not attr.startswith('__') and
                              not attr.startswith('_') and
                              self.__getattribute__(attr) in (None, 0)]
        return missing_properties


class SignalGeneratorBuilder:
    def __init__(self, signal_generator=None):
        if signal_generator is None:
            self.signal_generator = SignalGenerator()
        else:
            self.signal_generator = signal_generator

    @property
    def with_base_params(self):
        return SignalGeneratorBaseBuilder(self.signal_generator)

    @property
    def with_sampling_params(self):
        return SignalGeneratorSamplingBuilder(self.signal_generator)

    @property
    def with_noise_params(self):
        return SignalGeneratorNoiseBuilder(self.signal_generator)

    @property
    def with_transient_params(self):
        return SignalGeneratorTransientsBuilder(self.signal_generator)

    def build(self):
        return self.signal_generator

    def __str__(self):
        return self.signal_generator.__str__()


class SignalGeneratorBaseBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def base_amplitude(self, amplitude):
        self.signal_generator.base_amplitude = amplitude
        return self

    def base_frequency(self, frequency):
        self.signal_generator.base_frequency = frequency
        if self.signal_generator.num_diff_harmonics:
            self.signal_generator._possible_frequencies = [frequency * i for i in
                                                           range(1, self.signal_generator.num_diff_harmonics + 1)]
        return self

    def num_diff_harmonics(self, num_diff_harmonics):
        self.signal_generator.num_diff_harmonics = num_diff_harmonics
        if self.signal_generator.base_frequency:
            self.signal_generator._possible_frequencies = [self.signal_generator.base_frequency * i for i in
                                                           range(1, num_diff_harmonics + 1)]
        return self


class SignalGeneratorSamplingBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def duration(self, duration):
        self.signal_generator.duration = float(duration)
        if not (self.signal_generator.duration * self.signal_generator.samples_per_second).is_integer():
            raise SampleRateError
        return self

    def samples_per_second(self, samples_per_second):
        self.signal_generator.samples_per_second = float(samples_per_second)
        if not (self.signal_generator.duration * self.signal_generator.samples_per_second).is_integer():
            raise SampleRateError
        return self


class SignalGeneratorNoiseBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        # Note: Noise is gaussian by default
        super().__init__(signal_generator)
        signal_generator.noise_params = {
            'mean': None,
            'var': None,
        }

    def mean(self, mean):
        self.signal_generator.noise_params['mean'] = mean
        return self

    def var(self, var):
        self.signal_generator.noise_params['var'] = var
        return self


class SignalGeneratorTransientsBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def num_reg_trans(self, num_reg_trans):
        self.signal_generator.num_regular_transients = num_reg_trans
        return self

    def num_fail_trans(self, num_fail_trans):
        self.signal_generator.num_failure_transients = num_fail_trans
        return self
