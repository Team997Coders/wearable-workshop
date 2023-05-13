import math

import neopixel
import ema
from interfaces import IDisplay
import ulab.numpy as np
from spectrum_shared import map_power_to_range, map_normalized_value_to_color, linear_range,\
    map_float_color_to_neopixel_color, log_range, float_to_indicies, get_freq_powers_by_range, clip


class GraphDisplay(IDisplay):
    pixels: neopixel.NeoPixel
    num_rows: int
    num_cols: int
    pixel_indexer: Any # typing.Callable[[int, int], int]
    pixel_values: list[list[tuple[int, int, int]]] #Stores the values
    _range_indicies: np.array[int]
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

        # self.min_group_power_ema = []
        # self.max_group_power_ema = []
        # for i in range(0, self.num_cols):
        #     self.min_group_power_ema.append(ema.EMA(500, 2))
        #     self.max_group_power_ema.append(ema.EMA(500, 2))

        self.pixel_indexer = self.default_row_column_indexer if row_column_indexer is None else row_column_indexer
        self._range_indicies = None
        self._group_power = None

    def show(self, power_spectrum: np.array):
        if self._range_indicies is None:
            range = log_range(len(power_spectrum), self.num_total_groups)
            #range = linear_range(len(power_spectrum), self.num_total_groups)
            self._range_indicies = float_to_indicies(range)
            #print(f"Log range: {self._log_range_indicies}")

        std_spectrum = np.std(power_spectrum[128:])
        #print(f'std: {std_spectrum:0.3f}')

        self._group_power = get_freq_powers_by_range(power_spectrum,
                                                     self._range_indicies,
                                                     out=self._group_power)

        #group_power = get_log_freq_powers(power_spectrum, num_groups=self.num_total_groups)

        #next, write the new row of columns on the bottom row
        #print(f"{self._group_power}")
        #print(f'n_groups: {len(group_power)} n_cutoff: {self.num_cutoff_groups}')
        #print(f'Min: {self.last_min_group_power} Max: {self.last_max_group_power}')
        for i_col in range(self.num_cutoff_groups, len(self._group_power)):
            i = i_col
            while self._range_indicies[i] == self._range_indicies[i+1]:
                i -= 1  #Duplicate the previous columns output

            #print(f"iCol: {i} Power: {self._group_power[i]}")

            min_val = self.last_min_group_power[i] * 1.05 #Use the last min/max value before updating them
            max_val = self.last_max_group_power[i] * 0.95
            self.last_min_group_power[i] = min(self.last_min_group_power[i] * 1.0005, self._group_power[i]) #Slowly decay min/max
            self.last_max_group_power[i] = max(self.last_max_group_power[i] * .9995, self._group_power[i])

            if min_val == max_val:
                continue #Do not display since we don't have a range for the graph yet
 
            #The second-to-last column of lights is not to be trusted.  It must be watched.
            #if i == 6:
            #    print(f'{i_col} val: {self._group_power[i]} min: {self.last_min_group_power[i]} max: {self.last_max_group_power[i]}')

            norm_value = (self._group_power[i] - min_val) / (max_val - min_val)
            norm_value = clip(norm_value)

            #Tuning the line below can change how tall columns of lights appear.
            num_leds = int(math.ceil(self.num_rows * norm_value))
            if num_leds > self.num_rows:
                num_leds = self.num_rows

            i_range, norm_value = map_power_to_range(self._group_power[i], min_val, max_val)
            neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range, color_map=None)
            #print(f'{i_range} {norm_value} color: {neo_color}')
            for i_row in range(0, num_leds):
                i_pixel = self.pixel_indexer(i_row, i_col)
                if i_row == num_leds - 1: #Dim the highest point of the bar graph according to normalized value to simulate extra range
                    self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color, norm_value)
                else:
                    self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color)

                #print(f'{i_col},{i_row}: num_leds {num_leds} norm_val: {norm_value} neo_color: {neo_color} pix: {self.pixels[i_pixel]}')

            for i_row in range(num_leds, self.num_rows):
                i_pixel = self.pixel_indexer(i_row, i_col)
                #print(f'col: clear {i_col} row: {i_row} i_pix: {i_pixel} num_leds: {num_leds}')
                self.pixels[i_pixel] = (0, 0, 0)