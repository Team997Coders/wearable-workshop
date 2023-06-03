
try:
    import ulab.numpy as np
except ModuleNotFoundError:
    import numpy as np

import math


def clip(value: float, min_val: float = 0, max_val: float = 1.0) -> float:
    '''
    Returns the value, or min/max if value falls outside the provided range
    :param value:
    :param min_val:
    :param max_val:
    :return:
    '''
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value

def log_range(num_measurements: int, num_groups: int, base: float = None):
    '''Given a number of measurements and the desired grouping,
    returns the cutoff values to create bins evenly spaced in logarithmic space.
    '''
    log_range = math.log(num_measurements) if base is None else math.log(num_measurements, base)
    log_bin_spacing = log_range / num_groups
    log_bin_cutoffs = np.arange(0, num_groups+1)
    log_bin_cutoffs = log_bin_cutoffs * log_bin_spacing
    log_bin_cutoffs = np.exp(log_bin_cutoffs) if base is None else log_bin_cutoffs ** base
    #print(f'log_bin_cutoffs: {log_bin_cutoffs}')
    return log_bin_cutoffs

def linear_range(num_measurements: int, num_groups: int):
    '''Given a number of measurements and the desired grouping,
    returns the cutoff values to create bins evenly spaced in normal space.
    '''
    bin_spacing = num_measurements / num_groups
    bin_cutoffs = np.arange(0, num_groups+1) * bin_spacing
    bin_cutoffs[0] = 1  #Remove the first group, it isn't interesting
    #print(f"{bin_cutoffs[0:3]} {bin_cutoffs[-1]} len: {len(bin_cutoffs)}" )
    if num_groups + 1 != len(bin_cutoffs):
        raise ValueError("num_groups and len(bin_cutoffs) must match")
    return bin_cutoffs


def float_to_indicies(input: np.array):
    '''Convert a float array to an integer array that can be used for indexing
    '''
    input = np.around(input)  # Round cutoffs to nearest integer so we can use them as indicies
    return np.array(input, dtype=np.uint16)

def space_indicies(input: np.array):
    '''
    When there are duplicates in an index array, change the values so there are no duplicates
    :param input:
    :return:
    '''
    spaced_input = np.zeros(len(input), dtype=input.dtype)
    spaced_input[0] = input[0]
    for i in range(1, len(input)):
        if input[i] <= spaced_input[i - 1]:
            spaced_input[i] = spaced_input[i-1] + 1
        else:
            spaced_input[i] = input[i]

    return spaced_input

def get_freq_powers_by_range(spectrum: np.ndarray, range_cutoffs: np.ndarray[int], out: np.ndarray[float] | None = None):
    '''
    Using a pre-calculated set of indicies for each range return the summed power for each group
    :param spectrum:
    :param range_cutoffs:
    :param out:
    :return:
    '''
    num_groups = len(range_cutoffs) - 1
    if out is None:
        out = np.zeros((num_groups))  # Create a place to store the sum'ed power of each frequency range
    elif len(out) != num_groups:
        raise ValueError("Output array has the wrong shape")

    for i in range(0, num_groups):
        out[i] = np.sum(spectrum[range_cutoffs[i]:range_cutoffs[i + 1]])

    return out


# default_range_cutoffs = [0.15, 0.35, 0.65, 0.85, 1.0]
# default_base_color = [(0, 0, 0), #Red, Green, Blue weights for each range
#               (1, 0, 0),
#               (0, 1, 0),
#               (0, 0, 1),
#               (1, 1, 1)]

default_range_cutoffs = (0.10, 0.25, 0.45, 0.65, .85, 1.0)
default_base_color = ((0, 0, 0), #Red, Green, Blue weights for each range
                      (1, 0, 0),
                      (0, 1, 0),
                      (1, 1, 0),
                      (0, 1, 1),
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
    if colormap_index is None:
        raise ValueError('colormap_index must not be None')

    if normalized_value is None:
        raise ValueError('normalized_value must not be None')

    color_map = default_base_color if color_map is None else color_map
    if colormap_index >= len(color_map):
        raise ValueError("Number of range_cutoffs and number of color_map entries must match.")

    #Return a tuple for the normalized value, multiply each entry in the tuple by the color map
    return (normalized_value * color_map[colormap_index][0],
           normalized_value * color_map[colormap_index][1],
           normalized_value * color_map[colormap_index][2])

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
        return 0, 0

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

def map_float_color_to_neopixel_color(input: tuple[float], scalar: float | None = None) -> tuple[int]:
    '''
    Convert a tuple of values from 0 to 1 to a tuple of bytes from 0 to 255.  The
    output of this function can be passed to a neopixel to set a color
    :param value: tuple of three float values
    :param scalar: Optional, if included scales (multiplies) the color by the specified amount
    :return:
    '''
    scalar = 1.0 if scalar is None else scalar

    c =    int(input[0] * 255.0 * scalar), \
           int(input[1] * 255.0 * scalar), \
           int(input[2] * 255.0 * scalar)

    #print(f'{input} * {scalar} * 255 = {c}')
    return c

if __name__ == '__main__':
    freq = np.arange(0, 1000, 20)
    print(f'num freq: {len(freq)}')
    log_indicies = log_range(len(freq), 8, 2)
    print(f'log indicies: {log_indicies}')
    range_indicies = float_to_indicies(log_indicies)
    print(f'range indicies: {range_indicies}')
    si = space_indicies(range_indicies)
    print(f'spaced indicies: {si}')
