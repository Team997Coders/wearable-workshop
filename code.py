# This is a sample Python script.
import struct
import time
import asyncio
import analogio
import board
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import ulab.numpy as np
#import random
import neopixel
import math
from audiocore import WaveFile

import ulab.utils

import ema
from sound_rec import roll_buffer, prepend_buffer, record_sample
from basic_display import BasicDisplay
from waterfall_display import WaterfallDisplay
from graph_display import GraphDisplay

SAMPLE_RATE = 44000
SAMPLE_SIZE = 1 << 9  # Sample size must be a power of 2
SAMPLE_BITE_SIZE = SAMPLE_SIZE // 4  # How much of the sample window we replace each iteration

MIC_PIN = board.A1
MIC_ADC = analogio.AnalogIn(MIC_PIN)

NUM_NEO_ROWS = 4
NUM_NEO_COLS = 8
NUM_NEOS = NUM_NEO_COLS * NUM_NEO_ROWS


def ShowLightOrder(pixels: neopixel.NeoPixel, delay: float = None):
    '''
    Turn the pixels on in order to determine how they are numbered
    :param pixels: Neopixel controller
    :param delay: Delay before each pixel lights
    '''
    delay = 3.0 / float(NUM_NEOS) if delay is None else delay
    for i in range(0, NUM_NEOS):
        pixels[i] = (64, 0, 0)
        pixels.show()
        time.sleep(delay)

    for i in range(NUM_NEOS - 1, -1, -1):
        time.sleep(delay)
        pixels[i] = (0, 0, 0)
        pixels.show()


def reversing_row_column_indexer(irow, icol) -> int:
    '''
    Converts a row and column index into a neopixel index,
    each row reverses the order of the column indicies.  This is
    because the LED matrix is laid out in line that folds back on itself
    each row, ex:
    9 8 7 6 5
    0 1 2 3 4
    :param irow:
    :param icol:
    :return:
    '''
    adjusted_icol = icol if irow % 2 == 0 else (NUM_NEO_COLS - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    return (irow * NUM_NEO_COLS) + adjusted_icol

def flip_column_order_indexer(irow, icol) -> int:
    '''
    Flips the column ordering.  Useful when the left side of the display should be the right
    :param irow:
    :param icol:
    :return:
    '''
    adjusted_icol = (NUM_NEO_COLS - 1) - icol
    # print(f'irow: {irow} icol: {icol} adjusted_icol: {adjusted_icol}')
    return (irow * NUM_NEO_COLS) + adjusted_icol


# pixels = neopixel.NeoPixel(board.NEOPIXEL, n=NUM_NEOS, brightness=0.2, auto_write=False)
pixels = neopixel.NeoPixel(board.D6, n=NUM_NEOS, brightness=.05, auto_write=False)

async def Run(play_wave: bool):
    print(f"Hello World! Lets run main! play_wave: {play_wave}")
    #######################################################
    # Use reversing_row_column_indexer if your NeoPixels
    # initialize going back and forth like mowing the lawn.
    # Use None if your neopixel rows initalize in one
    # direction
    ShowLightOrder(pixels, 0.01)
    # row_indexer=reversing_row_column_indexer
    row_indexer = flip_column_order_indexer
    ########################################

    # Uncomment these lines to change how sound is displayed
    #display = BasicDisplay(pixels=pixels, num_groups=pixels.n, num_cutoff_groups=0)
    #display = WaterfallDisplay(pixels=pixels, num_cols=NUM_NEO_COLS, num_rows=NUM_NEO_ROWS,
    #                            num_cutoff_groups=0, row_column_indexer=row_indexer)

    display = GraphDisplay(pixels=pixels, num_cols=NUM_NEO_COLS, num_rows=NUM_NEO_ROWS, num_cutoff_groups=0, row_column_indexer=row_indexer)

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
        sample_buffer, sample_buffer_min, sample_buffer_max = asyncio.run(record_sample(MIC_ADC, SAMPLE_SIZE, sample_rate=SAMPLE_RATE, buffer=None))
        new_buffer = None

        #initialize the min/max values
        min_buffer_ema = ema.EMA(500, 2)
        max_buffer_ema = ema.EMA(500, 2)
        min_buffer_ema.add(sample_buffer_min)
        max_buffer_ema.add(sample_buffer_max)
        new_buffer_task = None #The async task to collect more data
        #print(f'Got first sample: {sample_buffer}')
        new_buffer_task = asyncio.create_task(
            record_sample(MIC_ADC, SAMPLE_SIZE, sample_rate=SAMPLE_RATE, buffer=new_buffer))
        while True:
            new_buffer, new_buffer_min, new_buffer_max = asyncio.run_until_complete(new_buffer_task)
            #new_buffer_task)

            new_buffer_task = asyncio.create_task(
                record_sample(MIC_ADC, SAMPLE_BITE_SIZE, sample_rate=SAMPLE_RATE, buffer=new_buffer))

            min_buffer_ema.add(new_buffer_min)
            max_buffer_ema.add(new_buffer_max)
            # print(f'new: {sample_buffer[0:5]}composite: {sample_buffer[SAMPLE_BITE_SIZE:SAMPLE_BITE_SIZE+5]}')
            sample_buffer = prepend_buffer(new_buffer, sample_buffer)
            buffer_range = max_buffer_ema.ema_value - min_buffer_ema.ema_value
            float_array = ((sample_buffer - min_buffer_ema.ema_value) / buffer_range) - 0.5
            #float_array = float_array / np.max(float_array)
            #print(f'float: {float_array[0:10]}')
            power_spectrum = ulab.utils.spectrogram(float_array)
            display.show(power_spectrum)
            pixels.show()

            sample_buffer = roll_buffer(sample_buffer, SAMPLE_BITE_SIZE)


            # time.sleep(0.5)

asyncio.run(Run(False))
