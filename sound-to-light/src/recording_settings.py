
class RecordingSettings():
    _sample_size: int #Must be a power of two
    _sample_rate: int
    _freq_cutoff: int #The highest frequency we want to display

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def sample_size(self) -> int:
        return self._sample_size

    @property
    def frequency_cutoff(self) -> int:
        return self._freq_cutoff

    @property
    def max_detectable_frequency(self) -> int:
        return self._sample_rate / 2.0

    def __init__(self, sampling_freq_hz: int, frequency_cutoff: int, sample_size_exp: int):
        self._sample_size = 1 << sample_size_exp
        self._sample_rate = sampling_freq_hz * 2
        self._freq_cutoff = frequency_cutoff

        if self._freq_cutoff > self.max_detectable_frequency:
            raise ValueError("Maximum frequency below requested frequency cutoff")

    def __str__(self) -> str:
        return f'max freq: {self.max_detectable_frequency} sample size: {self.sample_size}'