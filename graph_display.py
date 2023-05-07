import neopixel
import ema
from interfaces import IDisplay
import ulab.numpy as np
from spectrum_shared import map_power_to_range, map_normalized_value_to_color, \
    map_float_color_to_neopixel_color, get_log_freq_powers


class GraphDisplay(IDisplay):
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

        #next, write the new row of columns on the bottom row
        #print(f'n_groups: {len(group_power)} n_cutoff: {self.num_cutoff_groups}')
        for i_col in range(self.num_cutoff_groups, len(group_power)):
            i = i_col
            min_val = self.last_min_group_power[i] #Use the last min/max value before updating them
            max_val = self.last_max_group_power[i]
            self.last_min_group_power[i] = min(self.last_min_group_power[i] * 1.0005, group_power[i]) #Slowly decay min/max
            self.last_max_group_power[i] = max(self.last_max_group_power[i] * .9995, group_power[i])

            #print(f'min: {min_val:0.3f} max: {max_val:0.3f}')
            #self.last_min_group_power[i].add(min_val)
            #self.last_max_group_power[i].add(max_val)

            if min_val == max_val:
                continue #Do not display since we don't have a range for the graph yet

            #print(f'min: {self.last_min_group_power[i]} max: {self.last_max_group_power[i]}')
            norm_value = (group_power[i] - min_val) / (max_val - min_val)
            if norm_value < 0:
                norm_value = 0
            elif norm_value > 1.0:
                norm_value = 1.0

            num_leds = int(self.num_rows * norm_value + 1)
            if num_leds > self.num_rows:
                num_leds = self.num_rows

            i_range, norm_value = map_power_to_range(group_power[i], min_val, max_val)
            neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range, color_map=None)
            #print(f'{i_range} {norm_value} color: {neo_color}')
            for i_row in range(0, num_leds):
                i_pixel = self.pixel_indexer(i_row, i_col)
                if i_row == num_leds - 1: #Dim the highest point of the bar graph according to normalized value to simulate extra range
                    self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color, norm_value)
                else:
                    self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color)

            for i_row in range(num_leds, self.num_rows):
                i_pixel = self.pixel_indexer(i_row, i_col)
                #print(f'col: {i_col} row: {i_row} i_pix: {i_pixel} num_leds: {num_leds}')
                self.pixels[i_pixel] = (0,0,0)