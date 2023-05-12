import neopixel
from interfaces import IDisplay
import ulab.numpy as np
from spectrum_shared import map_float_color_to_neopixel_color, get_log_freq_powers, map_power_to_range, \
    map_normalized_value_to_color, log_range, float_to_indicies, get_freq_powers_by_range


waterfall_range_cutoffs = (0.3, 0.6, 0.7, 0.8, .9, 1.0)
waterfall_base_color = ((0, 0, 0), #Red, Green, Blue weights for each range
                      (1, 0, 0),
                      (0, 1, 0),
                      (1, 1, 0),
                      (0, 1, 1),
                      (1, 1, 1))

class WaterfallDisplay(IDisplay):
    pixels: neopixel.NeoPixel
    num_rows: int
    num_cols: int
    pixel_indexer: Any # typing.Callable[[int, int], int]
    pixel_values: list[list[tuple[int, int, int]]] #Stores the values
    _log_range_indicies: np.array[int]
    _group_power: np.array[float]

    def default_row_column_indexer(self, irow, icol) -> int:
        '''
        Converts a row and column index into a neopixel index
        :param irow:
        :param icol:
        :return:
        '''
        return (irow * self.num_cols) + icol

    @property
    def num_visible_groups(self) -> int:
        return self.num_cols

    @property
    def num_total_groups(self) -> int:
        return self.num_visible_groups + self.num_cutoff_groups

    def __init__(self, pixels: neopixel.NeoPixel, num_rows: int, num_cols: int, num_cutoff_groups: int,
                 row_column_indexer: Callable[[int, int], int] | None = None):
        self.pixels = pixels
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_cutoff_groups = num_cutoff_groups
        self.last_max_group_power = [0] * self.num_cols
        self.last_min_group_power = [1 << 16] * self.num_cols
        self.pixel_indexer = self.default_row_column_indexer if row_column_indexer is None else row_column_indexer
        self._log_range_indicies = None
        self._group_power = None

    def move_display_up_one_row(self):
        for i_row in range(self.num_rows-2, -1, -1):
            for i_col in range(0, self.num_cols):
                i_source = self.pixel_indexer(i_row, i_col)
                i_target = self.pixel_indexer(i_row+1, i_col)
                self.pixels[i_target] = self.pixels[i_source]

    def show(self, power_spectrum: np.array):
        if self._log_range_indicies is None:
            range = log_range(len(power_spectrum), self.num_total_groups)
            self._log_range_indicies = float_to_indicies(range)

        self._group_power = get_freq_powers_by_range(power_spectrum,
                                               self._log_range_indicies,
                                               out=self._group_power)

        #First, take all old pixel values, and move them up one row, except for the last row, which steps off the display
        self.move_display_up_one_row()

        #next, write the new row of columns on the bottom row
        #print(f'n_groups: {len(group_power)} n_cutoff: {self.num_cutoff_groups}')
        for i in range(self.num_cutoff_groups, len(self._group_power)):
            #print(f'i: {i}')
            i_pixel = self.pixel_indexer(0, i)
            min_val = self.last_min_group_power[i] * 1.05  # Use the last min/max value before updating them
            max_val = self.last_max_group_power[i] * .95
            self.last_min_group_power[i] = min(self.last_min_group_power[i] * 1.001, self._group_power[i])
            self.last_max_group_power[i] = max(self.last_max_group_power[i] * 0.999, self._group_power[i])
            #print(f'min: {min_val:0.3f} max: {max_val:0.3f}')
            i_range, norm_value = map_power_to_range(self._group_power[i], min_val, max_val, range_cutoffs=waterfall_range_cutoffs)
            if i_range is None:
                self.pixels[i_pixel] = (0, 0, 0)
            else:
                neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range, color_map=waterfall_base_color)

                #print(f'i: {i_pixel} val: {group_power[i]:0.3f} norm: {norm_value:0.3f}')
                self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color, norm_value)