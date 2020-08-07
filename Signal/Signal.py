import numpy as np


class Signal:
    def __init__(self, amplitude, frequency, phase=0):
        self.amplitude = amplitude
        self.frequency = frequency
        self.phase = phase

    def evaluate(self, duration, samples_per_second):
        # TODO make sure that duration*samples_per_seconds is integer is being called before
        sampling_times = np.array([i / samples_per_second for i in range(duration * samples_per_second)])
        evaluated_signal = self.amplitude * np.sin(2 * np.pi * self.frequency * sampling_times)
        return evaluated_signal

    def __str__(self):
        return 'Signal is composed of:\n' + \
               'Base params:\n' + \
               f'\tamplitude={self.amplitude}\n' + \
               f'\tfrequency={self.frequency}\n' + \
               f'\tphase={self.phase}\n'

#
# class SignalBuilder:
#     def __init__(self, signal=None):
#         if signal is None:
#             self.signal = Signal()
#         else:
#             self.signal = signal
#
#     @property
#     def with_base_params(self):
#         return SignalBaseBuilder(self.signal)
#
#     def __str__(self):
#         return self.signal.__str__()
#
#
# class SignalBaseBuilder(SignalBuilder):
#     def __init__(self, signal):
#         super().__init__(signal)
#
#     def base_freq(self, frequency):
#         self.signal.frequency = frequency
#         return self
#
#     def amplitude(self, amplitude):
#         self.signal.amplitude = amplitude
#         return self
#
#     def phase(self, phase):
#         self.signal.phase = phase
#         return self
#
# class PersonJobBuilder(PersonBuilder):
#     def __init__(self, person):
#         super().__init__(person)
#
#     def at(self, company_name):
#         self.person.company_name = company_name
#         return self
#
#     def as_a(self, position):
#         self.person.position = position
#         return self
#
#     def earning(self, annual_income):
#         self.person.annual_income = annual_income
#         return self
#
#
# class PersonAddressBuilder(PersonBuilder):
#     def __init__(self, person):
#         super().__init__(person)
#
#     def at(self, street_address):
#         self.person.street_address = street_address
#         return self
#
#     def with_postcode(self, postcode):
#         self.person.postcode = postcode
#         return self
#
#     def in_city(self, city):
#         self.person.city = city
#         return self
