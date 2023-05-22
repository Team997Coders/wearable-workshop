# This is a sample Python script.

import struct
import time
import asyncio
import board
import analogbufio
import array
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import ulab.numpy as np
#import random
import neopixel
from audiocore import WaveFile

import ulab.utils
import ema
import display_diagnostic
from recording_settings import RecordingSettings
from sound_rec import roll_buffer, prepend_buffer, record_sample_array, record_sample_numpy
from basic_display import BasicDisplay
from waterfall_display import WaterfallDisplay
from graph_display import GraphDisplay
from display_settings import DisplaySettings
from pixel_indexers import *


display_configs = {
    "32x8 Waterfall": DisplaySettings(num_rows=32, num_cols=8, pixel_indexer=columns_are_rows_with_alternating_column_order_indexer, log_scale=False),
    "8x32 Graph": DisplaySettings(num_rows=8, num_cols=32, pixel_indexer=rows_are_columns_with_alternating_reversed_column_order_indexer, log_scale=False),
    "8x4 Neopixel Feather Graph": DisplaySettings(num_rows=4, num_cols=8, pixel_indexer=flip_column_order_indexer, log_scale=True),
    "8x4 Neopixel Feather Waterfall": DisplaySettings(num_rows=4, num_cols=8, pixel_indexer=flip_column_order_indexer, log_scale=True),
    "4x16 Graph": DisplaySettings(num_rows=8, num_cols=32,
                                  pixel_indexer=rows_are_columns_with_alternating_reversed_column_order_indexer,
                                  num_neo_rows=8, num_neo_cols=32,
                                  log_scale=True),

}

sampling_settings = {
    "32x8 Waterfall": RecordingSettings(max_freq_hz=22000, frequency_cutoff=1280, sample_size_exp=10),
    "Low Frequency": RecordingSettings(max_freq_hz=22000, frequency_cutoff=400, sample_size_exp=10),
    "Low-Mid Frequency": RecordingSettings(max_freq_hz=22000, frequency_cutoff=800, sample_size_exp=10),
    "Broad Frequency": RecordingSettings(max_freq_hz=22000, frequency_cutoff=4000, sample_size_exp=10),
}

#This combo is a good starting point
#sample_settings = sampling_settings["Broad Frequency"]

sample_settings = sampling_settings["Broad Frequency"]

SAMPLE_BITE_SIZE = sample_settings.sample_size // 4  # How much of the sample window we replace each iteration

MIC_PIN = board.A1
#MIC_ADC = analogio.AnalogIn(MIC_PIN)

# pixels = neopixel.NeoPixel(board.NEOPIXEL, n=NUM_NEOS, brightness=0.2, auto_write=False)
pixels = neopixel.NeoPixel(board.D10, n=8*32, brightness=0.05, auto_write=False)
pixels_featherwing = neopixel.NeoPixel(board.D6, n=4*8, brightness=0.05, auto_write=False)

displays = (
    GraphDisplay(pixels, display_configs["8x32 Graph"], 0),
    WaterfallDisplay(pixels, display_configs["32x8 Waterfall"], 0),
    GraphDisplay(pixels_featherwing, display_configs["8x4 Neopixel Feather Graph"], 0),
    WaterfallDisplay(pixels_featherwing, display_configs["8x4 Neopixel Feather Waterfall"], 0),
    GraphDisplay(pixels, display_configs["4x16 Graph"], 0)
)

def get_frequencies(settings: RecordingSettings):
    '''
    Determine the frequency for each bin of an FFT performed with a
    recording sample with the provided settings
    :param settings:
    :return:
    '''
    frequency_bin_width = settings.sample_rate / settings.sample_size
    frequencies = np.arange(0, (frequency_bin_width * settings.sample_size) / 2.0, frequency_bin_width)
    print(f"bin width: {frequency_bin_width} n_samples: {settings.sample_size}\nfrequencies: {frequencies}")
    return frequencies

async def Run(play_wave: bool):
    #######################################################
    # Use reversing_row_column_indexer if your NeoPixels
    # initialize going back and forth like mowing the lawn.
    # Use None if your neopixel rows initalize in one
    # direction
    # row_indexer=reversing_row_column_indexer
     #ShowColumnOrder(pixels, row_indexer, 0)
    ########################################

    # Uncomment these lines to change how sound is displayed
    display = displays[4]

    #######################################################
    # If you have a new display the functions below can
    # help determine pixel order and if a pixel indexer
    # is addressing the pixels correctly
    #######################################################
    #display_diagnostic.ShowLightOrder(display.pixels, display.settings, 0.01)
    #display_diagnostic.ShowRowColumnOrder(display.pixels, display.settings, 0.0)
    #######################################################

    max_buffer_value = (1 << 16) - 1
    half_buffer_value = (1 << 15) #For some reason my mic defaults to half the max when it is quiet

    if play_wave:
        with open("StreetChicken.wav", "rb") as wave_file:
            sample_buffer = struct.unpack('H' * sample_settings.sample_size, wave_file.read(sample_settings.sample_size * 2))
            while True:
                sample_buffer = roll_buffer(sample_buffer, SAMPLE_BITE_SIZE)
                # print(f'rolled: {sample_buffer[0:10]}')
                # sample_buffer = get_sample(sample_buffer)
                new_buffer = struct.unpack('H' * SAMPLE_BITE_SIZE, wave_file.read(SAMPLE_BITE_SIZE * 2))
                # print(f'len sb {len(sample_buffer)} len nb {len(new_buffer)}')
                sample_buffer = np.array(prepend_buffer(new_buffer, sample_buffer))
                # print(f'composite: {sample_buffer[SAMPLE_BITE_SIZE:]}')
                # print(f'float array: {float_array}')
                power_spectrum = ulab.utils.spectrogram(sample_buffer / max_buffer_value)

                # print(f'len: {power_spectrum.shape} sum: {total_power} groups: {group_power} pix: {pixel_values}')
                display.show(power_spectrum)
                pixels.show()
    else:
        # Read the full buffer before we start displaying
        mic_buffer = array.array("H", [0x0000] * sample_settings.sample_size)
        mic_adc_bufferio = analogbufio.BufferedIn(MIC_PIN, sample_rate=sample_settings.sample_rate)
        mic_buffer_task = asyncio.create_task(record_sample_array(mic_adc_bufferio, sample_settings.sample_size, sample_settings.sample_rate, mic_buffer))
        sample_buffer = np.array(await mic_buffer_task)

        #initialize the min/max values
        #These values are used to normalize the recorded signal.  An exponential moving average is used to slowly
        #adjust the volume range that the microphone is focusing on.  A large number of samples means the range
        #adjusts slowly to changes in room sound.  Smaller values may adjust the range based on quiet stretces of
        #music or conversations and then saturate the diaplay when the volume increases.
        #smooth factor determines how much weight is given to the more recent records.  Use a
        #min_buffer_ema = ema.EMA(num_samples=1000, smooth=1.25)
        max_buffer_ema = ema.EMA(num_samples=500, smooth=1.5)

        frequencies = get_frequencies(sample_settings)
        max_freq_index = 0
        for i, freq in enumerate(frequencies):
            if freq > sample_settings.frequency_cutoff:
                break
            max_freq_index = i

        print(f'max freq index: {max_freq_index}')

        max_buffer_ema.add(np.max(sample_buffer))
        new_buffer_task = None #The async task to collect more data
        #print(f'Got first sample: {sample_buffer}')
        new_buffer_task = asyncio.create_task(
            record_sample_array(mic_adc_bufferio, sample_settings.sample_size, sample_rate=sample_settings.sample_rate, buffer=mic_buffer))
        while True:
            ###################
            # Sample Collection
            ###################

            #Wait for the audio sample to finish collecting
            mic_buffer = await new_buffer_task

            #Start a task to collect the audio sample
            new_buffer_task = asyncio.create_task(
                record_sample_array( mic_adc_bufferio, sample_settings.sample_size, sample_rate=sample_settings.sample_rate, buffer=mic_buffer))

            #########################
            #Process the audio sample
            #########################

            #Convert to a numpy.array
            sample_buffer = np.array(mic_buffer)
            #buffer_range = max_buffer_ema.ema_value - half_buffer_value

            #Adjust audio sample to a floating point array centered on 0
            #buffer_min = half_buffer_value #According to documentation no noise is halfway between the maximum value, so 2^15 for a range of 2^16
            #buffer_max = np.max(sample_buffer) #This should be the max of the absolute value, but abs is not built into Circuit Python
            #max_buffer_ema.add(buffer_max)

            #centering_adjustment = half_buffer_value + (buffer_range / 2)
            #print(f'max {buffer_max} min {buffer_min} range {buffer_range} centering_adjustment {centering_adjustment}')
            #sample_buffer -= centering_adjustment
            sample_buffer -= half_buffer_value

            power_spectrum = ulab.utils.spectrogram(sample_buffer)
            #print(f'cutoff index: {max_freq_index} power_spectrum: {power_spectrum[1:max_freq_index]}')
            #power_spectrum = power_spectrum[0:len(power_spectrum) // 2] # The array is mirrored, so only use half
            #power_spectrum = power_spectrum[len(power_spectrum) // 2:]  # The array is mirrored, so only use half

            display.show(power_spectrum[1:max_freq_index])
            #sample_buffer = roll_buffer(sample_buffer, SAMPLE_BITE_SIZE)
            # time.sleep(0.5)

asyncio.run(Run(False))