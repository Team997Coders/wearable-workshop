import math

import neopixel
import ema
from interfaces import IDisplay
import ulab.numpy as np
from display_settings import DisplaySettings
from spectrum_shared import map_power_to_range, map_normalized_value_to_color, linear_range,\
    map_float_color_to_neopixel_color, log_range, float_to_indicies, get_freq_powers_by_range, clip, space_indicies
import display_range

class GraphDisplay(IDisplay):
    pixels: neopixel.NeoPixel
    num_rows: int
    num_cols: int
    pixel_indexer: Any # typing.Callable[[int, int], int]
    pixel_values: list[list[tuple[int, int, int]]] #Stores the values
    _range_indicies: np.array[int]
    _group_power: np.array[float]
    settings: DisplaySettings

    @property
    def num_visible_groups(self) -> int:
        return self.num_cols

    @property
    def num_total_groups(self) -> int:
        return self.num_visible_groups + self.num_cutoff_groups

    def __init__(self, pixels: neopixel.NeoPixel, settings: DisplaySettings, num_cutoff_groups: int):
        self.pixels = pixels
        self.settings = settings
        self.num_rows = settings.num_rows
        self.num_cols = settings.num_cols
        self.pixel_indexer = settings.indexer
        self.num_cutoff_groups = num_cutoff_groups
        self._display_range = display_range.DisplayRange(self.num_cols)

        #self.pixel_indexer = self.default_row_column_indexer if row_column_indexer is None else row_column_indexer
        self._range_indicies = None
        self._group_power = None
        self._pixel_map = self._build_pixel_map()

    def _build_pixel_map(self):
        '''
        Create a map to move each pixel up one row.  This is considerably faster than calling a function
        for each pixel
        '''
        col_map = []
        for i_col in range(0, self.num_cols):
            row_map = []
            for i_row in range(0, self.num_rows):
                i_target = self.pixel_indexer(i_row, i_col, self.settings)
                row_map.append(i_target)
            col_map.append(tuple(row_map))

        return tuple(col_map)

    def _build_range_indicies(self, spectrum_len):
        if self.settings.log_scale:
            range = log_range(spectrum_len, self.num_total_groups)
        else:
            range = linear_range(spectrum_len, self.num_total_groups)

        range_indicies = float_to_indicies(range)
        range_indicies = space_indicies(range_indicies)
        #print(f"Range indicies: {range_indicies} nEntries: {len(range_indicies)}")
        return range_indicies

    def show(self, power_spectrum: np.array):
        # The first time this function is called we need to calculate the range indicies used for each group
        # Having the range indicies pre-calculated allows all later calls to execute faster and improve
        # display time
        if self._range_indicies is None:
            self._range_indicies = self._build_range_indicies(len(power_spectrum))

        # Create a histogram of power by
        self._group_power = get_freq_powers_by_range(power_spectrum,
                                                     self._range_indicies,
                                                     out=self._group_power)

        #self._group_power = self._group_power * (self._group_power / 2.0)

        #group_power = get_log_freq_powers(power_spectrum, num_groups=self.num_total_groups)

        #next, write the new row of columns on the bottom row
        #print(f"group power: {self._group_power} sum: {np.sum(self._group_power)}")


        #print(f'n_groups: {len(self._group_power)} n_cutoff: {self.num_cutoff_groups}')
        #print(f'Min: {self.last_min_group_power} Max: {self.last_max_group_power}')
        for i_col in range(self.num_cutoff_groups, len(self._group_power)):
            i = i_col

            if i + 1 >= len(self._range_indicies):
                break

            # Duplicate the previous columns output if there is no range available for this column
            # This is not used when there are enough columns to display  or if the space_indicies is
            # used on the _range_indicies
            while self._range_indicies[i] == self._range_indicies[i+1]:
                i += 1
                if i + 1 >= len(self._range_indicies):
                    break

            if i >= len(self._range_indicies) or i >= len(self._group_power):
                break
  
            #print(f"iCol: {i} Power: {self._group_power[i]}")


            # Use the min/max values from the last loop.  We are comparing the new power spectrum to the past, not to
            # its current value.

            min_val, max_val = self._display_range.get_group_minmax(i)

            #Rarely, (at startup), we have an identical min/max value.  For this case we do not light any column LEDs
            if min_val == max_val:
                norm_value = 0
            else:
                norm_value = (self._group_power[i] - min_val) / (max_val - min_val)
                norm_value = clip(norm_value)

            #Calculate how many LEDs in the column will be illuminated
            num_leds = int(math.ceil(self.num_rows * norm_value))
            if num_leds > self.num_rows:
                num_leds = self.num_rows

            #Convert the power to an LED color.  To do this we determine which entry in the color lookup table is used.
            i_range, norm_value = map_power_to_range(self._group_power[i], min_val, max_val)
            neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range, color_map=None)

            #Light each pixel in the column.  Look up the pixel's index, scale top pixel brightness according to normalized
            # value and set all pixels below the top to full brightness
            col_map = self._pixel_map[i_col]
            for i_row in range(0, num_leds):
                i_pixel = col_map[i_row]
                if i_row == num_leds - 1: #Dim the highest point of the bar graph according to normalized value to simulate extra range
                    self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color, norm_value)
                else:
                    self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color)

                #print(f'{i_col},{i_row}: num_leds {num_leds} norm_val: {norm_value} neo_color: {neo_color} pix: {self.pixels[i_pixel]}')

            # Any pixels not illuminated are now turned off
            for i_row in range(num_leds, self.num_rows):
                i_pixel = col_map[i_row]
                self.pixels[i_pixel] = (0, 0, 0)

        #print(f'min: {self.last_min_group_power} max: {self.last_max_group_power}')
        #Send the all pixel values to the NeoPixel display
        self.pixels.show()

        self._display_range.add(self._group_power)