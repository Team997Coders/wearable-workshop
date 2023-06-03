import neopixel
from interfaces import IDisplay
import ulab.numpy as np
import ema
from display_settings import DisplaySettings
from spectrum_shared import map_float_color_to_neopixel_color,  map_power_to_range, \
    map_normalized_value_to_color, log_range, float_to_indicies, get_freq_powers_by_range, \
    linear_range, space_indicies
import display_range

waterfall_range_cutoffs = (0.05, 0.20, 0.40, 0.60, .8, 1.0)
waterfall_base_color = ((0, 0, 0), #Red, Green, Blue weights for each range
                      (.25, 0, 0),
                      (0, .5, 0),
                      (.75, .75, 0),
                      (0, 1, 1),
                      (1, 1, 1))

class WaterfallDisplay(IDisplay):
    pixels: neopixel.NeoPixel
    settings: DisplaySettings
    num_rows: int
    num_cols: int
    pixel_indexer: any #  Callable[[int, int], int]
    pixel_values: list[list[tuple[int, int, int]]] #Stores the values
    _range_indicies: np.array[int]
    _group_power: np.array[float]

    @property
    def num_visible_groups(self) -> int:
        return self.num_cols

    @property
    def num_total_groups(self) -> int:
        return self.num_visible_groups + self.num_cutoff_groups

    def __init__(self, pixels: neopixel.NeoPixel, settings: DisplaySettings, num_cutoff_groups: int ):
        self.pixels = pixels
        self.settings = settings
        self.num_rows = settings.num_rows
        self.num_cols = settings.num_cols
        self.num_cutoff_groups = num_cutoff_groups
        self._display_range = display_range.DisplayRange(self.num_cols)
        self.pixel_indexer = settings.indexer
        self._range_indicies = None
        self._group_power = None
        self.move_up_one_row_map = self._build_move_pixel_map()

        self._mean_group_power_ema = []
        for i in range(0, self.num_cols):
            self._mean_group_power_ema.append(ema.EMA(500, 1.5))

    def _move_display_up_one_row(self) -> None:
        '''
        A helper function to move each row in the waterfall one step
        :return:
        '''

        for i_row in range(self.num_rows-2, -1, -1):
            col_map = self.move_up_one_row_map[i_row]
            for i_col in range(0, self.num_cols):
                i_source, i_target = col_map[i_col]
                self.pixels[i_target] = self.pixels[i_source]

                #i_source = self.pixel_indexer(i_row, i_col)
                #i_target = self.pixel_indexer(i_row+1, i_col)
                #self.pixels[i_target] = self.pixels[i_source]

    def _build_move_pixel_map(self) -> tuple[tuple[int, int]]:
        '''
        Create a lookup map to move each pixel up one row.  This is considerably faster than calling a function
        for each pixel to calculate an index
        '''
        row_map = []
        for i_row in range(0, self.num_rows-1):
            col_map = []
            for i_col in range(0, self.num_cols):
                i_source = self.pixel_indexer(i_row, i_col, self.settings)
                i_target = self.pixel_indexer(i_row+1, i_col, self.settings)
                col_map.append((i_source, i_target))
            row_map.append(tuple(col_map))
        return tuple(row_map)

    def show(self, power_spectrum: np.array):
        if self._range_indicies is None:
            if self.settings.log_scale:
                range = log_range(len(power_spectrum), self.num_total_groups)
            else:
                range = linear_range(len(power_spectrum), self.num_total_groups)

            self._range_indicies = float_to_indicies(range)
            self._range_indicies = space_indicies(self._range_indicies)

        self._group_power = get_freq_powers_by_range(power_spectrum,
                                                     self._range_indicies,
                                                     out=self._group_power)

        self._group_power = self._group_power * self._group_power

        #First, take all old pixel values, and move them up one row, except for the last row, which steps off the display
        self._move_display_up_one_row()

        #next, write the new row of columns on the bottom row
        #print(f'n_groups: {len(group_power)} n_cutoff: {self.num_cutoff_groups}')
        for i in range(self.num_cutoff_groups, len(self._group_power)):
            #print(f'i: {i}')
            self._mean_group_power_ema[i].add(self._group_power[i])
            i_pixel = self.pixel_indexer(0, i, self.settings)
            min_val, max_val = self._display_range.get_group_minmax(i)
            #print(f'min: {min_val:0.3f} max: {max_val:0.3f}')
            i_range, norm_value = map_power_to_range(self._group_power[i], min_val, max_val, range_cutoffs=waterfall_range_cutoffs)
            if i_range is None:
                self.pixels[i_pixel] = (0, 0, 0)
            else:
                neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range, color_map=waterfall_base_color)

                #print(f'i: {i_pixel} val: {group_power[i]:0.3f} norm: {norm_value:0.3f}')
                self.pixels[i_pixel] = map_float_color_to_neopixel_color(neo_color, norm_value)

        self.pixels.show()

        self._display_range.add(self._group_power)