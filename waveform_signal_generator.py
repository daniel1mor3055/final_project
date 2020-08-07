import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from apply_noise_method import ApplyNoiseMethod


def _single_sine_wave(amplitude, frequency, duration, samples_per_second):
    assert int(duration * samples_per_second) - duration * samples_per_second == 0, \
        "duration * samples_per_second must be an integer"

    sampling_times = np.array([i / samples_per_second for i in range(duration * samples_per_second)])
    result_sine_wave = amplitude * np.sin(2 * np.pi * frequency * sampling_times)
    return result_sine_wave


def _find_indicies_to_apply_noise(times_to_apply_noise, waveform_times):
    start_noise_index = -1
    end_noise_index = -1
    for index, time in enumerate(waveform_times):
        if time >= times_to_apply_noise[0] and start_noise_index == -1:
            start_noise_index = index
        if time <= times_to_apply_noise[1]:
            end_noise_index = index
    return start_noise_index, end_noise_index


def _get_indices_to_apply_noise_by_index(waveform, indices_to_apply_noise, apply_noise_all_waveform=False):
    if not apply_noise_all_waveform:
        assert isinstance(tuple, indices_to_apply_noise), "indices_to_apply_noise must be tuple of indices"
        start_noise_index = indices_to_apply_noise[0]
        end_noise_index = indices_to_apply_noise[1]
        return start_noise_index, end_noise_index
    else:
        start_noise_index = 0
        end_noise_index = len(waveform) - 1
        return start_noise_index, end_noise_index


def _get_indices_to_apply_noise_by_time(waveform, times_to_apply_noise, duration, samples_per_second,
                                        apply_noise_all_waveform=False):
    sampling_times = np.array([i / samples_per_second for i in range(duration * samples_per_second)])
    if not apply_noise_all_waveform:
        assert times_to_apply_noise[0] > sampling_times[0] and times_to_apply_noise[1] < sampling_times[-1] \
            , "interval of applying noise doesn't match waveform domain"

        start_noise_index, end_noise_index = _find_indicies_to_apply_noise(
            times_to_apply_noise=times_to_apply_noise,
            waveform_times=sampling_times)
        return start_noise_index, end_noise_index
    else:
        start_noise_index = 0
        end_noise_index = len(waveform) - 1
        return start_noise_index, end_noise_index


def add_noise_to_waveform(waveform, noise_params, apply_noise_method, duration, samples_per_second,
                          times_to_apply_noise=None, indices_to_apply_noise=None, apply_noise_all_waveform=False):
    assert isinstance(noise_params, tuple), "noise params should contain (mean,var) params"
    assert isinstance(apply_noise_method, Enum) and (
            apply_noise_method.value in (0, 1)), "apply_noise_method should be enum(0: BY-TIME,1: BY-INDEX)"

    if apply_noise_method == ApplyNoiseMethod.BY_TIME:
        assert (
                       times_to_apply_noise is not None) or apply_noise_all_waveform, "times_to_apply_noise should be given while applying noise by time"
        start_noise_index, end_noise_index = _get_indices_to_apply_noise_by_time(waveform=waveform,
                                                                                 times_to_apply_noise=times_to_apply_noise,
                                                                                 duration=duration,
                                                                                 samples_per_second=samples_per_second,
                                                                                 apply_noise_all_waveform=apply_noise_all_waveform)
    else:
        assert (
                       indices_to_apply_noise is not None) or apply_noise_all_waveform, "indices_to_apply_noise should be given while applying noise by index"
        start_noise_index, end_noise_index = _get_indices_to_apply_noise_by_index(waveform=waveform,
                                                                                  indices_to_apply_noise=indices_to_apply_noise,
                                                                                  apply_noise_all_waveform=apply_noise_all_waveform)
    mean, var = noise_params
    noisy_waveform = waveform.copy()
    for i in range(start_noise_index, end_noise_index + 1):
        noisy_waveform[i] = waveform[i] + np.random.normal(mean, var)

    return noisy_waveform


def _multi_sine_waveforms(amplitudes, frequencies, duration, samples_per_second):
    assert len(amplitudes) == len(frequencies), "len(amplitudes)!=len(frequencies)"
    assert isinstance(duration, (float, int)), "duration must be of types=(float,int)"
    assert isinstance(samples_per_second, int), "samples_per_second must be of type int"

    result_waveform = None
    for i in range(len(frequencies)):
        single_sine_wave = _single_sine_wave(amplitudes[i], frequencies[i], duration, samples_per_second)
        if result_waveform is None:
            result_waveform = single_sine_wave
        else:
            result_waveform += single_sine_wave

    return result_waveform


def _check_indices_validity(lst_of_indices, total_number_of_samples):
    minimum_samples_in_interval = total_number_of_samples // 5

    all_intervals_are_valid = all([lst_of_indices[i + 1] - lst_of_indices[i] >= minimum_samples_in_interval for i in
                                   range(len(lst_of_indices) - 1)])
    last_interval_valid = total_number_of_samples - lst_of_indices[-1] >= minimum_samples_in_interval
    first_interval_valid = lst_of_indices[0] >= minimum_samples_in_interval
    all_indices_are_different = (len(lst_of_indices) == len(set(lst_of_indices)))

    return all_indices_are_different and all_intervals_are_valid and last_interval_valid and first_interval_valid


def _get_different_indices_to_apply_transients(number_of_transients, duration, samples_per_second):
    total_number_of_samples = duration * samples_per_second

    all_indices_are_different = False
    lst_of_different_indices = list()
    while not all_indices_are_different:
        lst_of_different_indices = list()
        for i in range(number_of_transients):
            lst_of_different_indices.append(np.random.randint(total_number_of_samples))
        lst_of_different_indices.sort()
        all_indices_are_different = _check_indices_validity(lst_of_different_indices, total_number_of_samples)

    return lst_of_different_indices


def _create_signal_with_load_transients(number_of_load_transients, lst_of_different_signals,
                                        indices_to_apply_transients, duration, samples_per_second):
    signal_with_load_transients = np.zeros(duration * samples_per_second)
    start_index = 0
    for i in range(number_of_load_transients):
        signal_with_load_transients[start_index:indices_to_apply_transients[i]] = lst_of_different_signals[i][
                                                                                  start_index:
                                                                                  indices_to_apply_transients[i]]
        start_index = indices_to_apply_transients[i]
    signal_with_load_transients[start_index:] = lst_of_different_signals[-1][start_index:]
    return signal_with_load_transients


def create_signal_with_load_transients(number_of_transients, duration, samples_per_second, max_number_of_harmonics=100,
                                       base_freq=1):
    number_of_different_harmonics = 10
    mean = 0
    var = 1
    assert int(duration * samples_per_second) == duration * samples_per_second, \
        "duration*samples_per_second must be an integer"

    indices_to_apply_transients = _get_different_indices_to_apply_transients(number_of_transients=number_of_transients,
                                                                             duration=duration,
                                                                             samples_per_second=samples_per_second)

    lst_of_different_signals = list()
    frequencies = [base_freq * i for i in range(1, number_of_different_harmonics + 1)]
    for i in range(number_of_transients + 1):

        counts_of_different_harmonics = np.zeros(number_of_different_harmonics)
        draws = np.abs(np.random.normal(mean, var, size=max_number_of_harmonics))
        for i in range(len(draws)):
            counts_of_different_harmonics[int(draws[i] / (var / 2))] += 1

        amplitudes = [count / number_of_different_harmonics for count in counts_of_different_harmonics]
        multi_sine_waveform = _multi_sine_waveforms(amplitudes=amplitudes, frequencies=frequencies,
                                                    duration=duration, samples_per_second=samples_per_second)
        lst_of_different_signals.append(multi_sine_waveform)

    signal_with_load_transients = _create_signal_with_load_transients(number_of_load_transients=number_of_transients,
                                                                      lst_of_different_signals=lst_of_different_signals,
                                                                      indices_to_apply_transients=indices_to_apply_transients,
                                                                      duration=duration,
                                                                      samples_per_second=samples_per_second)
    return signal_with_load_transients, indices_to_apply_transients


def add_failure_trans(waveform, max_duration_of_failure_trans, duration, samples_per_second):
    duration_of_fail_trans = np.random.uniform(0.1, max_duration_of_failure_trans)
    fail_trans_start_time = np.random.uniform(1, duration - 1)
    fail_trans_end_time = fail_trans_start_time + duration_of_fail_trans
    mean, var = (0, 3)
    signal_with_fail_trans = add_noise_to_waveform(waveform=waveform, noise_params=(mean, var),
                                                   apply_noise_method=ApplyNoiseMethod.BY_TIME, duration=duration,
                                                   samples_per_second=samples_per_second,
                                                   times_to_apply_noise=(fail_trans_start_time, fail_trans_end_time))
    return signal_with_fail_trans


def create_realistic_signal(num_of_load_trans, duration, samples_per_second):
    signal_with_load_trans, indices_of_load_trans = create_signal_with_load_transients(duration=duration,
                                                                                       number_of_transients=num_of_load_trans,
                                                                                       samples_per_second=samples_per_second)

    signal_with_load_trans = add_noise_to_waveform(waveform=signal_with_load_trans, noise_params=(0, 0.1),
                                                   apply_noise_method=ApplyNoiseMethod.BY_TIME, duration=duration,
                                                   samples_per_second=samples_per_second, apply_noise_all_waveform=True)

    signal_with_fail_trans = add_failure_trans(waveform=signal_with_load_trans, max_duration_of_failure_trans=1,
                                               duration=duration, samples_per_second=samples_per_second)

    return signal_with_fail_trans, signal_with_load_trans, indices_of_load_trans
