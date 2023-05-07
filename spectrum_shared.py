import ulab.numpy as np
import math


def log_range(num_measurements: list[float], num_groups: int):
    '''Given a number of measurements and the desired grouping,
    returns the cutoff values to create bins evenly spaced in logarithmic space.
    '''
    log_range = math.log(num_measurements)
    log_bin_spacing = log_range / num_groups
    log_bin_cutoffs = np.arange(0, num_groups+1)
    log_bin_cutoffs = log_bin_cutoffs * log_bin_spacing
    log_bin_cutoffs = np.exp(log_bin_cutoffs)
    return log_bin_cutoffs

def get_log_freq_powers(spectrum: np.ndarray, num_groups: int):
    '''
    Divided a spectrum into num_groups evenly spaced on the log axis
    :param spectrum: Frequency spectrum
    :param num_groups: Desired number of groups
    :return:
    '''
    lr = log_range(len(spectrum), num_groups)
    #print(f"log: {lr} spec: {spectrum}")
    lr = np.ceil(lr) #Round cutoffs to nearest integer so we can use them as indicies
    #print(f'{lr}')
    groups = np.zeros((num_groups)) # Create a place to store the sum'ed power of each frequency range
    for i in range(0, num_groups):
        groups[i] = np.sum(spectrum[int(lr[i]):int(lr[i+1])])
        #print(f"log cutoffs: {int(lr[i])}:{int(lr[i+1])} {spectrum[int(lr[i]):int(lr[i+1])]}")

    return groups

def get_freq_powers(spectrum: np.ndarray, num_groups: int):
    '''
    Divided a spectrum into num_groups
    :param spectrum: Frequency spectrum
    :param num_groups: Desired number of groups
    :return:
    '''
    group_sample_size = int(spectrum.shape[0] // num_groups)
    groups = np.zeros((num_groups))
    for i in range(0, num_groups):
        groups[i] = np.sum(spectrum[i:i+group_sample_size])

    return groups

# default_range_cutoffs = [0.15, 0.35, 0.65, 0.85, 1.0]
# default_base_color = [(0, 0, 0), #Red, Green, Blue weights for each range
#               (1, 0, 0),
#               (0, 1, 0),
#               (0, 0, 1),
#               (1, 1, 1)]

default_range_cutoffs = (0.15, 0.25, 0.45, 0.65, .85, 1.0)
default_base_color = ((0, 0, 0), #Red, Green, Blue weights for each range
                      (0, 0, 1),
                      (0, 1, 0),
                      (1, 1, 0),
                      (1, 0, 0),
                      (1, 1, 1))

def map_normalized_value_to_color(normalized_value: float, colormap_index: int, color_map: list[tuple[float]] | None = None):
    '''

    :param value: value to convert to an RGB tuple
    :param min: min possible value
    :param max: max possible value
    :param ranges: range cutoffs to assign a value to a colormap range
    :param color_map: a colormap that multiples the value, after normalizing it within its range, to a color
    :return: A tuple of three integers, mapping RGB, with 0 representing OFF and 255 representing fully ON
    '''
    color_map = default_base_color if color_map is None else color_map
    if colormap_index >= len(color_map):
        raise ValueError("Number of range_cutoffs and number of color_map entries must match.")

    #Return a tuple for the normalized value, multiply each entry in the tuple by the color map
    return (normalized_value * color_map[colormap_index][0] * 255,
           normalized_value * color_map[colormap_index][1] * 255,
           normalized_value * color_map[colormap_index][2] * 255)

    raise ValueError("Value outside of color map range")

def map_power_to_range(value: float, min_val: float, max_val: float, range_cutoffs: list[float] | None = None):
    '''
    Given a power, map it into a specific range.
    :param value: value to convert to an RGB tuple
    :param min_val: min possible value
    :param max_val: max possible value
    :param ranges: range cutoffs to assign a value to a colormap range
    :return: A tuple containing the index of the range the pixel mapped into and the normalized value of the
    pixel within that range.  For example, if the range array was [0, 5, 10] and the value 7.5 is passed, the
    return value is (1, 0.5), indicating the value maps to the second entry in the range array and is halfway
    through that range.
    '''
    range_cutoffs = default_range_cutoffs if range_cutoffs is None else range_cutoffs
    range = max_val - min_val
    if range == 0:
        return None, None

    value = (value - min_val) / range
    #print(f'value -> {value}')
    if value < 0:
        return 0, 0

    if value > 1.0:
        return len(range_cutoffs) - 1, 1.0

    for i, cutoff in enumerate(range_cutoffs):
        if value > cutoff:
            continue

        # Normalize where this value lives in the range and represent it as a number between 0 and 1.
        # For example, if the range is 3 to 9, and the value is 6, the normalized_value is 0.5.

        range_normalized_value = (value - range_cutoffs[i-1]) / (range_cutoffs[i] - range_cutoffs[i-1])
        #print(f'v: {value - range_cutoffs[i-1]} r: {range_cutoffs[i] - range_cutoffs[i-1]}')

        #Return a tuple for the normalized value, multiply each entry in the tuple by the color map
        return i, range_normalized_value

    raise ValueError("Value outside of color map range")

def map_power_to_color(value: float, min_val: float, max_val: float, range_cutoffs: list[float] | None = None,  color_map: list[tuple[float]] | None = None):
    i_range, norm_value = map_power_to_range(value, min_val, max_val)
    return map_normalized_value_to_color(norm_value, i_range, color_map=None)


def map_float_color_to_neopixel_color(input: tuple[float], scalar: float | None = None) -> tuple[int]:
    '''
    Convert a tuple of values from 0 to 1 to a tuple of bytes from 0 to 255.  The
    output of this function can be passed to a neopixel to set a color
    :param value: tuple of three float values
    :param scalar: Optional, if included scales (multiplies) the color by the specified amount
    :return:
    '''
    scalar = 1 if scalar is None else scalar

    return (int(input[0] * 255 * scalar),
            int(input[1] * 255 * scalar),
            int(input[2] * 255 * scalar))