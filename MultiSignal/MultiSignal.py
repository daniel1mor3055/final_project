from Signal.signal_exceptions import SampleRateError
from MultiSignal.multi_signal_exceptions import AmplitudesFrequenciesMatchError
from Signal.Signal import SignalBuilder


class MultiSignals:
    def __init__(self):
        self.signals = []
        self.duration =0
        self.samples_per_seconds=0

    @classmethod
    def from_signal(cls, signals):
        multi_signals = cls()
        
        multi_signals.signals = signals
        return multi_signals

    @classmethod
    def from_params_lists(cls, amplitudes, frequencies, duration, samples_per_seconds):
        if len(amplitudes) != len(frequencies):
            raise AmplitudesFrequenciesMatchError

        signals = []

    def add_signal(self,amplitude,frequency,):

    def __str__(self):
        return '\n'.join([signal.__str__() for signal in self.signals])


class SignalBuilder:
    def __init__(self, signal=None):
        if signal is None:
            self.signal = Signal()
        else:
            self.signal = signal

    @property
    def with_base_params(self):
        return SignalBaseBuilder(self.signal)

    # @property
    # def works(self):
    #     return SignalJobBuilder(self.signal)

    def build(self):
        return self.signal

    def __str__(self):
        return self.signal.__str__()


class SignalBaseBuilder(SignalBuilder):
    def __init__(self, signal):
        super().__init__(signal)

    def base_freq(self, frequency):
        self.signal.frequency = frequency
        return self

    def amplitude(self, amplitude):
        self.signal.amplitude = amplitude
        return self

    def duration(self, duration):
        self.signal.duration = float(duration)
        if not (self.signal.duration * self.signal.samples_per_second).is_integer():
            raise SampleRateError
        return self

    def samples_per_second(self, samples_per_second):
        self.signal.samples_per_second = float(samples_per_second)
        if not (self.signal.duration * self.signal.samples_per_second).is_integer():
            raise SampleRateError
        return self
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
