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
from sound_rec import roll_buffer, prepend_buffer, record_sample_array, record_sample_numpy
from basic_display import BasicDisplay
from waterfall_display import WaterfallDisplay
from graph_display import GraphDisplay
from display_settings import DisplaySettings
from pixel_indexers import *


display_configs = {
    "32x8 Waterfall": DisplaySettings(32, 8, columns_are_rows_with_alternating_column_order_indexer),
    "8x32 Graph": DisplaySettings(8, 32, rows_are_columns_with_alternating_column_order_indexer),
    "8x4 Neopixel Feather Graph": DisplaySettings(4, 8, flip_column_order_indexer),
    "8x4 Neopixel Feather Waterfall": DisplaySettings(4, 8, flip_column_order_indexer)
}

FREQUENCY_CUTOFF = 11000 # How fast we sample the signal in Hz (waves per second)
SAMPLE_RATE = int(FREQUENCY_CUTOFF * 2.1)
SAMPLE_SIZE = 1 << 9  # Sample size must be a power of 2
SAMPLE_BITE_SIZE = SAMPLE_SIZE // 4  # How much of the sample window we replace each iteration

MIC_PIN = board.A1
#MIC_ADC = analogio.AnalogIn(MIC_PIN)

NUM_NEO_ROWS = 8
NUM_NEO_COLS = 32
NUM_NEOS = NUM_NEO_COLS * NUM_NEO_ROWS

# pixels = neopixel.NeoPixel(board.NEOPIXEL, n=NUM_NEOS, brightness=0.2, auto_write=False)
pixels = neopixel.NeoPixel(board.D10, n=NUM_NEOS, brightness=0.05, auto_write=False)
pixels_featherwing = neopixel.NeoPixel(board.D6, n=4*8, brightness=0.05, auto_write=False)

displays = (
    GraphDisplay(pixels, display_configs["8x32 Graph"], 0),
    WaterfallDisplay(pixels, display_configs["32x8 Waterfall"], 0),
    GraphDisplay(pixels_featherwing, display_configs["8x4 Neopixel Feather Graph"], 0),
    WaterfallDisplay(pixels_featherwing, display_configs["8x4 Neopixel Feather Waterfall"], 0),
)

def ShowLightOrder(pixels: neopixel.NeoPixel, settings: DisplaySettings, delay: float = None):
    '''
    Turn the pixels on in order to determine how they are numbered
    :param pixels: Neopixel controller
    :param delay: Delay before each pixel lights
    '''
    delay = 3.0 / float(settings.num_neos) if delay is None else delay
    for i in range(0, settings.num_neos):
        pixels[i] = (64, 0, 0)
        pixels.show()
        time.sleep(delay)

    for i in range(settings.num_neos - 1, -1, -1):
        time.sleep(delay)
        pixels[i] = (0, 0, 0)
        pixels.show()

def ShowColumnOrder(pixels: neopixel.NeoPixel, settings: DisplaySettings, delay: float = None):
    '''
    Light each column from 0 to N starting lighting each row 0 to M
    :param pixels: Neopixel controller
    :param delay: Delay before each pixel lights
    '''
    delay = 3.0 / float(settings.num_neos) if delay is None else delay
    for icol in range(0, settings.num_cols):
        for irow in range(0, settings.num_rows):
            i = settings.indexer(irow, icol, settings)
            pixels[i] = (64, 0, 0)
            pixels.show()
            time.sleep(delay)

    for icol in range(0, settings.num_cols):
        for irow in range(0, settings.num_rows):
            i = settings.indexer(irow, icol, settings)
            pixels[i] = (0, 0, 0)
    pixels.show()

async def Run(play_wave: bool):
    print(f"Hello World! Lets run main! play_wave: {play_wave}")
    #######################################################
    # Use reversing_row_column_indexer if your NeoPixels
    # initialize going back and forth like mowing the lawn.
    # Use None if your neopixel rows initalize in one
    # direction
    # row_indexer=reversing_row_column_indexer
     #ShowColumnOrder(pixels, row_indexer, 0)
    ########################################

    # Uncomment these lines to change how sound is displayed
    display = displays[1]

    #ShowLightOrder(display.pixels, display.settings, 0.01)
    ShowColumnOrder(display.pixels, display.settings, 0.0)
    #######################################################

    max_buffer_value = (1 << 16) - 1
    min_buffer_value = 0
    half_buffer_value = (1 << 15) #For some reason my mic defaults to half the max when it is quiet

    if play_wave:
        print("Hello World! Lets play a WAV!")
        with open("StreetChicken.wav", "rb") as wave_file:
            sample_buffer = struct.unpack('H' * SAMPLE_SIZE, wave_file.read(SAMPLE_SIZE * 2))
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
        #print("Hello World! Lets record sound!")
        # Read the full buffer before we start displaying
        #sample_buffer, sample_buffer_min, sample_buffer_max = asyncio.run(record_sample(MIC_ADC, SAMPLE_BITE_SIZE, sample_rate=SAMPLE_RATE, buffer=None))
        new_buffer = None
        mic_buffer = array.array("H", [0x0000] * SAMPLE_SIZE)
        mic_adc_bufferio = analogbufio.BufferedIn(MIC_PIN, sample_rate=SAMPLE_RATE)
        mic_buffer_task = asyncio.create_task(record_sample_array(mic_adc_bufferio, SAMPLE_SIZE, SAMPLE_RATE, mic_buffer))
        sample_buffer = np.array(await mic_buffer_task)

        #initialize the min/max values
        #These values are used to normalize the recorded signal.  An exponential moving average is used to slowly
        #adjust the volume range that the microphone is focusing on.  A large number of samples means the range
        #adjusts slowly to changes in room sound.  Smaller values may adjust the range based on quiet stretces of
        #music or conversations and then saturate the diaplay when the volume increases.
        #smooth factor determines how much weight is given to the more recent records.  Use a
        min_buffer_ema = ema.EMA(num_samples=300, smooth=1.5)
        max_buffer_ema = ema.EMA(num_samples=300, smooth=1.5)

        min_buffer_ema.add(np.min(sample_buffer))
        max_buffer_ema.add(np.max(sample_buffer))
        new_buffer_task = None #The async task to collect more data
        #print(f'Got first sample: {sample_buffer}')
        new_buffer_task = asyncio.create_task(
            record_sample_array(mic_adc_bufferio, SAMPLE_SIZE, sample_rate=SAMPLE_RATE, buffer=mic_buffer))
        while True:
            #Start a task to collect the audio sample.
            #mic_buffer = await asyncio.gather(new_buffer_task)

            mic_buffer = await new_buffer_task

            new_buffer_task = asyncio.create_task(
                record_sample_array(mic_adc_bufferio, SAMPLE_SIZE, sample_rate=SAMPLE_RATE, buffer=mic_buffer))
            sample_buffer = np.array(mic_buffer)

            buffer_min = np.min(sample_buffer)
            buffer_max = np.max(sample_buffer)
            min_buffer_ema.add(np.min(sample_buffer))
            max_buffer_ema.add(np.max(sample_buffer))
            #print(f'new: {sample_buffer[0:5]}composite: {sample_buffer[SAMPLE_BITE_SIZE:SAMPLE_BITE_SIZE+5]}')
            #sample_buffer = prepend_buffer(new_buffer, sample_buffer)
            #buffer_range = max_buffer_ema.ema_value - min_buffer_ema.ema_value
            buffer_range = buffer_max - buffer_min
            centering_adjustment = buffer_min + (buffer_range // 2)
            #print(f'max {buffer_max} min {buffer_min} range {buffer_range} centering_adjustment {centering_adjustment}')
            float_array = sample_buffer - centering_adjustment
            #float_array = float_array / np.max(float_array)
            #print(f'float: {float_array[0:10]}')
            power_spectrum = ulab.utils.spectrogram(float_array)
            power_spectrum = power_spectrum[0:len(power_spectrum) // 2] # The array is mirrored, so only use half
            #power_spectrum = power_spectrum[len(power_spectrum) // 2:]  # The array is mirrored, so only use half
            display.show(power_spectrum)
            #sample_buffer = roll_buffer(sample_buffer, SAMPLE_BITE_SIZE)
            # time.sleep(0.5)

asyncio.run(Run(False))