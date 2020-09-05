import numpy as np
import random

from MultiSignal.MultiSignal import MultiSignal
from SignalGenerator.signal_generator_constants import (
    NUM_DRAWS_AMPLITUDES_DIFF_HARMONICS,
    MIN_SAMPLES_IN_INTERVAL_LIMITER,
    EXTRACT_AMPLITUDES_NOISE_PARAMS,
    MAX_DIST_IN_STANDARD_DEVIATION,
)
from SignalGenerator.signal_generator_exceptions import (
    MissingPropertiesError,
    FailureTransParamsError
)
from SignalGenerator.signal_generator_exceptions import SampleRateError


class SignalGenerator:
    def __init__(self):
        self.base_amplitudes = None
        self.base_frequency = None
        self.num_diff_harmonics = None
        self.noise_params = None
        self.duration = None
        self.samples_per_second = None
        self.num_fail_trans = None
        self.min_gap_between_fail_trans = None
        self.fail_trans_noise_params = None
        self.fail_trans_max_samples = None
        self.fail_trans_min_samples = None
        self.fail_trans_gap_from_start_end_samples = None
        self.load_trans_noise_params = None
        self.load_trans_samples_apply_noise = None
        self._possible_frequencies = None
        self._total_num_samples = None
        self._fail_trans_intervals = None
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
                                   f'\tnum failure transients={self.num_fail_trans}\n' + \
                                   f'\tmin gap between fail transients={self.min_gap_between_fail_trans}\n' + \
                                   f'\tfailure transients noise parameters={self.fail_trans_noise_params}\n' + \
                                   f'\tfail trans max samples={self.fail_trans_max_samples}\n' + \
                                   f'\tfail trans min samples={self.fail_trans_min_samples}\n' + \
                                   f'\tfail trans gap from stand and end samples={self.fail_trans_gap_from_start_end_samples}\n' + \
                                   f'\tload transients noise parameters={self.load_trans_noise_params}\n' + \
                                   f'\tload transients samples to apply noise={self.load_trans_samples_apply_noise}\n'

        return assigned_properties_repr + (missing_properties_repr if missing_properties else '')

    def generate(self):
        missing_properties = self._get_missing_properties()
        if missing_properties:
            raise MissingPropertiesError(missing_properties)

        generated_signal = self._create_signal_with_load_transients()
        self._add_noise_to_signal(generated_signal, self.noise_params)
        self._add_failure_trans(generated_signal)
        return generated_signal

    def _validate_fail_trans_locations(self, fail_trans_start_indices, fail_trans_end_indices):
        fail_transients_intervals = [(start_index, end_index) for start_index, end_index in
                                     zip(fail_trans_start_indices, fail_trans_end_indices)]
        fail_transients_intervals.sort(key=lambda tup: tup[0])
        for i in range(1, len(fail_transients_intervals)):
            curr_interval_start_index, curr_interval_end_index = fail_transients_intervals[i]
            prev_interval_start_index, prev_interval_end_index = fail_transients_intervals[i - 1]
            if curr_interval_start_index > prev_interval_end_index + self.min_gap_between_fail_trans:
                continue
            return False

        return True

    def _add_failure_trans(self, signal_with_load_transients):
        # TODO maybe its smarter to determine the number of samples of the transients based on our sample rate/ #samples
        valid_choice = False
        fail_trans_start_indices, fail_trans_end_indices = None, None
        while not valid_choice:
            fail_trans_num_samples = np.random.randint(self.fail_trans_min_samples, self.fail_trans_max_samples,
                                                       size=self.num_fail_trans)

            earliest_possible_start, latest_possible_end = self.fail_trans_gap_from_start_end_samples, \
                                                           self._total_num_samples - fail_trans_num_samples - self.fail_trans_gap_from_start_end_samples

            fail_trans_start_indices = np.random.randint(earliest_possible_start, latest_possible_end,
                                                         size=self.num_fail_trans)

            fail_trans_end_indices = fail_trans_start_indices + fail_trans_num_samples

            valid_choice = self._validate_fail_trans_locations(fail_trans_start_indices, fail_trans_end_indices)

        self._fail_trans_intervals = sorted(list(zip(fail_trans_start_indices, fail_trans_end_indices)),
                                            key=lambda tup: tup[0])
        for start_index, end_index in self._fail_trans_intervals:
            self._add_noise_to_signal(signal_with_load_transients, self.fail_trans_noise_params, start_index, end_index)

    @staticmethod
    def _add_noise_to_signal(signal, noise_params, start_index=None, end_index=None):
        start_index, end_index = start_index or 0, end_index or len(signal)
        mean, var = noise_params['mean'], noise_params['var']

        for i in range(start_index, end_index):
            signal[i] = signal[i] + np.random.normal(mean, var)

    @staticmethod
    def _add_noise_to_signal_multiple_indices(signal, noise_params, lst_start_end_indices):
        for start_index, end_index in lst_start_end_indices:
            SignalGenerator._add_noise_to_signal(signal, noise_params, start_index, end_index)

    def _create_signal_with_load_transients(self):
        lst_clean_signals = self._create_clean_signals()
        break_indices_for_load_transients = self._get_break_signal_indices()
        signal_with_load_transients = self._determine_load_transients(break_indices_for_load_transients,
                                                                      lst_clean_signals)
        indices_to_apply_load_noise = []
        for index in break_indices_for_load_transients:
            indices_to_apply_load_noise.append(
                (index - self.load_trans_samples_apply_noise, index + self.load_trans_samples_apply_noise))

        SignalGenerator._add_noise_to_signal_multiple_indices(signal_with_load_transients, self.load_trans_noise_params,
                                                              indices_to_apply_load_noise)

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

        tail_copy = amplitudes_diff_harmonics[1:]
        random.shuffle(tail_copy)
        amplitudes_diff_harmonics[1:] = tail_copy

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
    def with_load_transient_params(self):
        return SignalGeneratorLoadTransientsBuilder(self.signal_generator)

    @property
    def with_fail_transient_params(self):
        return SignalGeneratorFailTransientsBuilder(self.signal_generator)

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

        if self.signal_generator.samples_per_second:
            if self.signal_generator.samples_per_second % frequency != 0:
                raise SampleRateError(message='Samples per second must be a multiplication of base frequency')
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
                raise SampleRateError(message='duration*samples_per_second must be an integer')
            else:
                self.signal_generator._total_num_samples = int(duration * self.signal_generator.samples_per_second)

        return self

    def samples_per_second(self, samples_per_second):
        self.signal_generator.samples_per_second = samples_per_second
        if self.signal_generator.duration:
            if not float(self.signal_generator.duration * self.signal_generator.samples_per_second).is_integer():
                raise SampleRateError(message='duration*samples_per_second must be an integer')
            else:
                self.signal_generator._total_num_samples = int(samples_per_second * self.signal_generator.duration)

        if self.signal_generator.base_frequency:
            if samples_per_second % self.signal_generator.base_frequency != 0:
                raise SampleRateError(message='Samples per second must be a multiplication of base frequency')
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


class SignalGeneratorFailTransientsBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def min_gap_between_fail_trans(self, min_gap):
        self.signal_generator.min_gap_between_fail_trans = min_gap
        return self

    def num_fail_trans(self, num_fail_trans):
        self.signal_generator.num_fail_trans = num_fail_trans
        return self

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

    def max_failure_trans_samples(self, max_failure_trans_samples):
        if self.signal_generator.fail_trans_min_samples:
            if self.signal_generator.fail_trans_min_samples > max_failure_trans_samples:
                raise FailureTransParamsError(
                    message='min_failure_trans samples should be lower than max_failure_trans_samples')
        self.signal_generator.fail_trans_max_samples = max_failure_trans_samples
        return self

    def min_failure_trans_samples(self, min_failure_trans_samples):
        if self.signal_generator.fail_trans_max_samples:
            if self.signal_generator.fail_trans_max_samples < min_failure_trans_samples:
                raise FailureTransParamsError(
                    message='min_failure_trans samples should be lower than max_failure_trans_samples')
        self.signal_generator.fail_trans_min_samples = min_failure_trans_samples
        return self

    def gap_from_start_end_samples(self, gap_from_start_end_samples):
        self.signal_generator.fail_trans_gap_from_start_end_samples = gap_from_start_end_samples
        return self


class SignalGeneratorLoadTransientsBuilder(SignalGeneratorBuilder):
    def __init__(self, signal_generator):
        super().__init__(signal_generator)

    def mean_load_trans(self, mean):
        if not self.signal_generator.load_trans_noise_params:
            self.signal_generator.load_trans_noise_params = {
                'mean': None,
                'var': None,
            }
        self.signal_generator.load_trans_noise_params['mean'] = mean
        return self

    def var_load_trans(self, var):
        if not self.signal_generator.load_trans_noise_params:
            self.signal_generator.load_trans_noise_params = {
                'mean': None,
                'var': None,
            }
        self.signal_generator.load_trans_noise_params['var'] = var
        return self

    def samples_to_apply_noise(self, samples_to_apply_noise):
        self.signal_generator.load_trans_samples_apply_noise = samples_to_apply_noise
        return self
