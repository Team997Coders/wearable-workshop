# This is a sample Python script.
import time

import board
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import ulab.numpy as np
import random
import neopixel
import math

import ulab.utils

SAMPLE_RATE = 44000
SAMPLE_SIZE = 1024 #Sample size must be a power of 2

NUM_NEOS = 1

pixels = neopixel.NeoPixel(board.NEOPIXEL, n=NUM_NEOS, brightness=0.2, auto_write=False)

def get_sample(buffer: np.ndarray | None = None):
    if buffer is None:
        buffer = np.zeros((SAMPLE_SIZE))

    time_offset = time.monotonic() % 50
    time_offset_squared = time_offset * time_offset

    for i in range(0, buffer.shape[0]):
        buffer[i] = math.cos(time_offset_squared * i) + math.sin(time_offset * i) #math.sin((i / SAMPLE_SIZE) * math.pi * 2) + math.cos(time_offset_squared * i)
        #buffer[i] = 0.5

    return buffer

def get_freq_powers(spectrum: np.ndarray, num_groups: int):
    group_sample_size = int(spectrum.shape[0] / num_groups)
    groups = np.zeros((num_groups))
    for i in range(0, num_groups):
        offset = i * group_sample_size
        groups[i] = np.sum(spectrum[i:i+group_sample_size])

    return groups

sample_buffer = None
while True:
    sample_buffer = get_sample(sample_buffer)
    power_spectrum = ulab.utils.spectrogram(sample_buffer)

    #Divide the power spectrum into a number of chunks according to the number of lights we have
    group_power = get_freq_powers(power_spectrum, num_groups=3)
    total_power = np.sum(group_power)

    #pixel_values = tuple(np.ceil((group_power / total_power) * 255))
    #print(f'len: {power_spectrum.shape} sum: {total_power} groups: {group_power} pix: {pixel_values}')
    #pixels[0] = pixel_values


    min_group_power = np.min(group_power)
    max_group_power = np.max(group_power)
    pixel_values = [0,0,0]
    for i in range(0, len(group_power)):
        if group_power[i] == min_group_power:
            pixel_values[i] = 0
        elif group_power[i] == max_group_power:
            pixel_values[i] = 255
        else:
            pixel_values[i] = int(((group_power[i] - min_group_power) / (max_group_power - min_group_power)) * 255)

    pixels[0] = pixel_values
    print(f'len: {power_spectrum.shape} sum: {total_power} groups: {group_power} pix: {pixel_values}')
    pixels.show()
