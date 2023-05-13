class RecordingSettings():
    frequency_cutoff_hz: int
    sample_size: int #Must be a power of two

    @property
    def sample_rate(self):
        return self.frequency_cutoff_hz * 2.1

    def __init__(self, freq_hz: int, sample_size_exp: int):
        self.sample_size = 1 << sample_size_exp
        self.frequency_cutoff_hz = freq_hz