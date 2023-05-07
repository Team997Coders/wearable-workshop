import math
import ulab.numpy as np
import neopixel
from spectrum_shared import get_freq_powers, map_power_to_color, map_float_color_to_neopixel_color, get_log_freq_powers, \
    map_power_to_range, map_normalized_value_to_color
from interfaces import IDisplay


class BasicDisplay(IDisplay):
    last_min_group_power: float
    last_max_group_power: float
    pixels: neopixel.NeoPixel
    num_groups: int  # How many groups we display, defaults to number of pixels
    num_cutoff_groups: int  # How many low frequency groups we ignore

    @property
    def total_groups(self) -> int:
        return self.num_groups + self.num_cutoff_groups

    def __init__(self, pixels: neopixel.NeoPixel, num_groups: int, num_cutoff_groups: int = 20):
        self.pixels = pixels
        self.num_groups = num_groups
        self.num_cutoff_groups = num_cutoff_groups
        self.last_max_group_power = [0] * self.total_groups
        self.last_min_group_power = [5000] * self.total_groups



    def show(self, power_spectrum):
        group_power = get_log_freq_powers(power_spectrum, num_groups=self.num_groups+self.num_cutoff_groups)

        for i in range(self.num_cutoff_groups, len(group_power)):
            min_val = self.last_min_group_power[i]  # Use the last min/max value before updating them
            max_val = self.last_max_group_power[i]
            self.last_min_group_power[i] = min(self.last_min_group_power[i] * 1.0005, group_power[i])
            self.last_max_group_power[i] = max(self.last_max_group_power[i] * .9995, group_power[i])
            i_range, norm_value = map_power_to_range(group_power[i], min_val, max_val)
            if i_range is None:
                continue

            neo_color = map_normalized_value_to_color(normalized_value=norm_value, colormap_index=i_range,
                                                      color_map=None)
            self.pixels[i - self.num_cutoff_groups] = map_float_color_to_neopixel_color(neo_color, norm_value)