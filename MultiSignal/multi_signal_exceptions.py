class AmplitudesFrequenciesMatchError(Exception):
    def __init__(self, message='Amplitudes and frequencies dimensions do not match'):
        super().__init__(message)
