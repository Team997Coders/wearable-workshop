from collections import namedtuple
import neopixel

class DisplaySettings():
    num_rows: int
    num_cols: int
    num_neo_cols: int
    num_neo_rows: int
    indexer: Callable[[int, int], int]

    @property
    def num_neos(self):
        return self.num_rows * self.num_cols

    def __init__(self, num_rows: int, num_cols: int, pixel_indexer, num_neo_rows: int = None, num_neo_cols: int = None):
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.num_neo_rows = num_rows if num_neo_rows is None else num_neo_rows
        self.num_neo_cols = num_cols if num_neo_cols is None else num_neo_cols
        self.indexer = pixel_indexer


