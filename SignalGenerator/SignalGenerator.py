from SignalGenerator.signal_generator_constants import (
    NUM_DRAWS_AMPLITUDES_DIFF_HARMONICS,
    MIN_SAMPLES_IN_INTERVAL_LIMITER,
    EXTRACT_AMPLITUDES_NOISE_PARAMS,
    MIN_FAILURE_TRANS_SAMPLES,
    MAX_FAILURE_TRANS_SAMPLES,
    GAP_FROM_START_END_TRANS_SAMPLES,
    MAX_DIST_IN_STANDARD_DEVIATION,
)
from SignalGenerator.signal_generator_exceptions import (
    SampleRateError,
    MissingPropertiesError
)

from MultiSignal.MultiSignal import MultiSignal
import numpy as np


class SignalGenerator:
    def __init__(self):
        self.base_amplitudes = None
        self.base_frequency = None
        self.num_diff_harmonics = None
        self.noise_params = None
        self.duration = None
        self.samples_per_second = None
        self.fail_trans_noise_params = None
        self._possible_frequencies = None
        self._total_num_samples = None
        self._num_regular_transients = None

    def __str__(self):
        missing_properties = self._get_missing_properties()
        missing_properties_repr = 'SignalGenerator still missing the following parameters:\n\t' + \
                                  '\n\t'.join(missing_properties)

        assigned_properties_repr = 'SignalGenerator has the following parameters:\n' + \
                                   f'\tbase frequency={self.base_frequency}\n' + \
                                   f'\tbase amplitude={self.base_amplitudes}\n' + \
                                   f'\tnum of different harmonics={self.num_diff_harmonics}\n' + \
                                   f'\tnoise parameters={self.noise_params}\n' + \
                                   f'\tduration={self.duration}\n' + \
                                   f'\tsamples per seconds={self.samples_per_second}\n' + \
                                   f'\tfailure transients noise parameters={self.fail_trans_noise_params}\n'

        return assigned_properties_repr + (missing_properties_repr if missing_properties else '')

    def generate(self):
        missing_properties = self._get_missing_properties()
        if missing_properties:
            raise MissingPropertiesError(missing_properties)

        generated_signal = self._create_signal_with_load_transients()
        self._add_noise_to_signal(generated_signal, self.noise_params)
        self._add_failure_trans(generated_signal)
        return generated_signal

    def _add_failure_trans(self, signal_with_load_transients):
        # TODO maybe its smarter to determine the number of samples of the transients based on our sample rate/ #samples
        fail_trans_indices = np.random.randint(MIN_FAILURE_TRANS_SAMPLES, MAX_FAILURE_TRANS_SAMPLES)
        fail_trans_start_index = np.random.randint(GAP_FROM_START_END_TRANS_SAMPLES,
                                                   self._total_num_samples - fail_trans_indices - GAP_FROM_START_END_TRANS_SAMPLES)
        fail_trans_end_index = fail_trans_start_index + fail_trans_indices
        self._add_noise_to_signal(signal_with_load_transients, self.fail_trans_noise_params, fail_trans_start_index,
                                  fail_trans_end_index)

    @staticmethod
    def _add_noise_to_signal(signal, noise_params, start_index=None, end_index=None):
        start_index, end_index = start_index or 0, end_index or len(signal)
        mean, var = noise_params['mean'], noise_params['var']

        for i in range(start_index, end_index):
            signal[i] = signal[i] + np.random.normal(mean, var)

    def _create_signal_with_load_transients(self):
        lst_clean_signals = self._create_clean_signals()
        break_indices_for_load_transients = self._get_break_signal_indices()
        signal_with_load_transients = self._determine_load_transients(break_indices_for_load_transients,
                                                                      lst_clean_signals)
        return signal_with_load_transients

    def _determine_load_transients(self, break_indices_for_load_transients, lst_clean_signals):
        signal_with_load_transients = np.zeros(self._total_num_samples)
        start_index = 0
        for i in range(self._num_regular_transients):
            signal_with_load_transients[start_index:break_indices_for_load_transients[i]] = \
                lst_clean_signals[i][start_index:break_indices_for_load_transients[i]]
            start_index = break_indices_for_load_transients[i]
        signal_with_load_transients[start_index:] = lst_clean_signals[-1][start_index:]
        return signal_with_load_transients

    def _get_break_signal_indices(self):
        break_indices_valid = False
        optional_diff_indices = None
        while not break_indices_valid:
            optional_diff_indices = [np.random.randint(self._total_num_samples) for i in
                                     range(self._num_regular_transients)]
            optional_diff_indices.sort()
            break_indices_valid = self._verify_indices(optional_diff_indices)

        return optional_diff_indices

    def _verify_indices(self, lst_indices_to_verify):
        min_samples_in_interval = self._total_num_samples // \
                                  (self._num_regular_transients + MIN_SAMPLES_IN_INTERVAL_LIMITER)
        lst_indices_to_verify.insert(0, 0)
        lst_indices_to_verify.append(self._total_num_samples)
        all_intervals_are_valid = all(
            [lst_indices_to_verify[i + 1] - lst_indices_to_verify[i] >= min_samples_in_interval for i in
             range(len(lst_indices_to_verify) - 1)])
        lst_indices_to_verify.pop()
        lst_indices_to_verify.pop(0)

        all_indices_are_different = (len(lst_indices_to_verify) == len(set(lst_indices_to_verify)))

        return all_intervals_are_valid and all_indices_are_different

    def _create_clean_signals(self):
        # TODO in this way, most of our signals will look pretty much the same. Need to ask Yuval about common behaviors
        lst_clean_signals = list()
        for i in range(self._num_regular_transients + 1):
            amplitudes_diff_harmonics = self._extract_amplitudes_with_respect_to_harmonics(signal_index=i)

            multi_signal = MultiSignal.from_params_lists(amplitudes_diff_harmonics, self._possible_frequencies)
            multi_signal_evaluated = multi_signal.evaluate(self.duration, self.samples_per_second)
            lst_clean_signals.append(multi_signal_evaluated)

        return lst_clean_signals

    def _extract_amplitudes_with_respect_to_harmonics(self, signal_index):
        mean, var = EXTRACT_AMPLITUDES_NOISE_PARAMS['mean'], EXTRACT_AMPLITUDES_NOISE_PARAMS['var']
        counts_different_harmonics = np.zeros(self.num_diff_harmonics)
        draws = np.abs(np.random.normal(mean, var, size=NUM_DRAWS_AMPLITUDES_DIFF_HARMONICS))
        for draw in draws:
            counts_different_harmonics[
                int(draw / ((MAX_DIST_IN_STANDARD_DEVIATION * var ** 0.5) / self.num_diff_harmonics))] += 1

        count_base_amplitude = counts_different_harmonics[0]
        amplitudes_diff_harmonics = [count * self.base_amplitudes[signal_index] / count_base_amplitude for count in
                                     counts_different_harmonics]

        return amplitudes_diff_harmonics

    def _get_missing_properties(self):
        missing_properties = [attr for attr in dir(self) if
                              not attr.startswith('__') and
                              not attr.startswith('_') and
                              self.__getattribute__(attr) is None]
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
    def with_fail_transient_params(self):
        return SignalGeneratorTransientsBuilder(self.signal_generator)

    def build(self):
        return self.signal_generator

    def __str__(self):
        return self.signal_generator.__str__()


class SignalGeneratorBaseBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def base_amplitudes(self, amplitudes):
        self.signal_generator.base_amplitudes = amplitudes
        self.signal_generator._num_regular_transients = len(amplitudes) - 1
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
        self.signal_generator.duration = duration
        if self.signal_generator.samples_per_second:
            if not float(self.signal_generator.duration * self.signal_generator.samples_per_second).is_integer():
                raise SampleRateError
            else:
                self.signal_generator._total_num_samples = int(duration * self.signal_generator.samples_per_second)
        return self

    def samples_per_second(self, samples_per_second):
        self.signal_generator.samples_per_second = samples_per_second
        if self.signal_generator.duration:
            if not float(self.signal_generator.duration * self.signal_generator.samples_per_second).is_integer():
                raise SampleRateError
            else:
                self.signal_generator._total_num_samples = int(samples_per_second * self.signal_generator.duration)
        return self


class SignalGeneratorNoiseBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        # Note: Noise is gaussian by default
        super().__init__(signal_generator)

    def mean(self, mean):
        if not self.signal_generator.noise_params:
            self.signal_generator.noise_params = {
                'mean': None,
                'var': None,
            }
        self.signal_generator.noise_params['mean'] = mean
        return self

    def var(self, var):
        if not self.signal_generator.noise_params:
            self.signal_generator.noise_params = {
                'mean': None,
                'var': None,
            }
        self.signal_generator.noise_params['var'] = var
        return self


class SignalGeneratorTransientsBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def mean_fail_trans(self, mean):
        if not self.signal_generator.fail_trans_noise_params:
            self.signal_generator.fail_trans_noise_params = {
                'mean': None,
                'var': None,
            }
        self.signal_generator.fail_trans_noise_params['mean'] = mean
        return self

    def var_fail_trans(self, var):
        if not self.signal_generator.fail_trans_noise_params:
            self.signal_generator.fail_trans_noise_params = {
                'mean': None,
                'var': None,
            }
        self.signal_generator.fail_trans_noise_params['var'] = var
        return self
