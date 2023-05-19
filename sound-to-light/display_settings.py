from collections import namedtuple
import neopixel

class DisplaySettings():
    _num_rows: int
    _num_cols: int
    _num_neo_cols: int
    _num_neo_rows: int
    _indexer: Callable[[int, int], int]
    _log_scale: bool

    @property
    def num_cols(self) -> int:
        return self._num_cols

    @property
    def num_rows(self) -> int:
        return self._num_rows

    @property
    def num_neo_cols(self) -> int:
        return self._num_neo_cols

    @property
    def num_neo_rows(self) -> int:
        return self._num_neo_rows

    @property
    def log_scale(self) -> bool:
        return self._log_scale

    @property
    def indexer(self):
        return self._indexer

    @property
    def num_neos(self):
        return self.num_rows * self.num_cols

    def __init__(self, num_rows: int, num_cols: int, pixel_indexer, log_scale: bool,
                 num_neo_rows: int = None, num_neo_cols: int = None):
        self._num_cols = num_cols
        self._num_rows = num_rows
        self._num_neo_rows = num_rows if num_neo_rows is None else num_neo_rows
        self._num_neo_cols = num_cols if num_neo_cols is None else num_neo_cols
        self._indexer = pixel_indexer
        self._log_scale = log_scale


