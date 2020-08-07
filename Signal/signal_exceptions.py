class SampleRateError(ValueError):
    def __init__(self, message='duration*samples_per_second must be an integer'):
        super().__init__(message)
