import neopixel
from interfaces import IDisplay
import ulab.numpy as np
from spectrum_shared import map_float_color_to_neopixel_color, get_log_freq_powers, map_power_to_range, \
    map_normalized_value_to_color


class WaterfallDisplay(IDisplay):
    pixels: neopixel.NeoPixel
    num_rows: int
    num_cols: int
    pixel_indexer: Any # typing.Callable[[int, int], int]
    pixel_values: list[list[tuple[int, int, int]]] #Stores the values

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

    def show(self, power_spectrum: np.array):
        group_power = get_log_freq_powers(power_spectrum, num_groups=self.num_total_groups)

        #First, take all old pixel values, and move them up one row, except for the last row, which steps off the display
        for i_row in range(self.num_rows-2, -1, -1):
            #print(f'i_row: {i_row}')
            for i_col in range(0, self.num_cols):

                i_source = self.pixel_indexer(i_row, i_col)
                i_target = self.pixel_indexer(i_row+1, i_col)
                #print(f'  {i_col} t: {i_target} s: {i_source}')
                self.pixels[i_target] = self.pixels[i_source]


        #next, write the new row of columns on the bottom row
        #print(f'n_groups: {len(group_power)} n_cutoff: {self.num_cutoff_groups}')
        for i in range(self.num_cutoff_groups, len(group_power)):
            #print(f'i: {i}')
            i_pixel = self.pixel_indexer(0, i)
            min_val = self.last_min_group_power[i] * 1.05  # Use the last min/max value before updating them
            max_val = self.last_max_group_power[i] * .95
            self.last_min_group_power[i] = min(self.last_min_group_power[i] * 1.001, group_power[i])
            self.last_max_group_power[i] = max(self.last_max_group_power[i] * 0.999, group_power[i])
            print(f'min: {min_val:0.3f} max: {max_val:0.3f}')
            i_range, norm_value = map_power_to_range(group_power[i], min_val, max_val)
            if i_range is None:
                self.pixels[i_pixel] = (0, 0, 0)
            else:
                neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range, color_map=None)

                #print(f'i: {i_pixel} val: {group_power[i]:0.3f} norm: {norm_value:0.3f}')
                self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color, norm_value)