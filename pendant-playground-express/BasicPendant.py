# BasicPendant.py
# Translated to python by Ian, Arduino code written by Tom Saska.
#
#

# Import the needed libraries
import time
import math
import board
import digitalio
from rainbowio import colorwheel
import audiobusio
import adafruit_fancyled.fastled_helpers as helper
import neopixel


NUM_LEDS = 10
brightness = 30.0/255.0 # initial brightness
min_brightness = 10.0/255.0
max_brightness = 180/255.0
brightness_int = 40.0/255.0

# number of audio samples to read at one time.
NUM_SAMPLES = 100
SCALE_EXPONENT = math.pow(10, 2*-0.1)

steps = 10 # makes the rainbow colors more or less spread out
NUM_MODES = 6 # change this number if you add or subtract modes

######################## Setup needed hardware

# setup the neopixel strip
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_LEDS, brightness=0.2, auto_write=False)


# setup the microphone
mic = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                       sample_rate=16000, bit_depth=16)


# setup the needed buttons
leftButton = digitalio.DigitalInOut(board.BUTTON_A)
leftButton.switch_to_input(pull=digitalio.Pull.DOWN)
rightButton = digitalio.DigitalInOut(board.BUTTON_B)
rightButton.switch_to_input(pull=digitalio.Pull.DOWN)

###################### Setup needed variables.
# These are global variables, which you should typically avoid, but are useful in these small
# programs. Try to avoid using them in the future.

# initial mode
ledMode = 0
leftButtonPressed = False # button pressed
rightButtonPressed = False

# initial location
startIndex = 0
pallete = None

# audio sample array
# This uses the slightly confusing python array library rather than a list for speed.
# 'H' indicates it is an unsigned short
# [0] * NUM_SAMPLES defines the starting array entries (NUM_SAMPLES 0's)
samples = array.array('H', [0] * NUM_SAMPLES)

#################### Define FastLED color palletes using python FancyLED.

## Setup color palletes
RainbowColors_p = [ 0xFF0000, 0xD52A00, 0xAB5500, 0xAB7F00,
                    0xABAB00, 0x56D500, 0x00FF00, 0x00D52A,
                    0x00AB55, 0x0056AA, 0x0000FF, 0x2A00D5,
                    0x5500AB, 0x7F0081, 0xAB0055, 0xD5002B]

OceanColors_p = [   CRGB::MidnightBlue,
                    CRGB::DarkBlue,
                    CRGB::MidnightBlue,
                    CRGB::Navy,
               
                    CRGB::DarkBlue,
                    CRGB::MediumBlue,
                    CRGB::SeaGreen,
                    CRGB::Teal,

                    CRGB::CadetBlue,
                    CRGB::Blue,
                    CRGB::DarkCyan,
                    CRGB::CornflowerBlue,

                    CRGB::Aquamarine,
                    CRGB::SeaGreen,
                    CRGB::Aqua,
                    CRGB::LightSkyBlue]


# Sound reactive setup
# Based on Adafruit VU meter code
# https://learn.adafruit.com/adafruit-circuit-playground-express/playground-sound-meter

# Restrict value to be between floor and ceiling.
def constrain(value, floor, ceiling):
    return max(floor, min(value, ceiling))


# Scale input_value between output_min and output_max, exponentially.
def log_scale(input_value, input_min, input_max, output_min, output_max):
    normalized_input_value = (input_value - input_min) / \
                             (input_max - input_min)
    return output_min + \
        math.pow(normalized_input_value, SCALE_EXPONENT) \
        * (output_max - output_min)


# Remove DC bias before computing RMS.
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )

    return math.sqrt(samples_sum / len(values))


def mean(values):
    return sum(values) / len(values)


def volume_color(volume):
    return 200, volume * (255 // NUM_LEDS), 0


# Record an initial sample to calibrate. Assume it's quiet when we start.
mic.record(samples, len(samples))
# Set lowest level to expect, plus a little.
input_floor = normalized_rms(samples) + 10
# OR: used a fixed floor
# input_floor = 50

# You might want to print the input_floor to help adjust other values.
# print(input_floor)

# Corresponds to sensitivity: lower means more pixels light up with lower sound
# Adjust this as you see fit.
input_ceiling = input_floor + 500


######### define custom functions

# rainbow function
def rainbow():
    global startIndex
    startIndex += 1 # this sets the motion speed.
    if startIndex >= 255:
        startIndex = 0

    FillLEDsFromPaletteColors(startIndex)

    pixels.show()
    time.show(0.02)

def FillLEDsFromPaletteColors(colorIndex):
    global palette

    # go through each pixels and set the color
    for i in range(NUM_LEDS):
        pixels[i] = helper.ColorFromPalette(palette, colorIndex, brightness, blend=True)


# directly taken from adafruit code.
# https://learn.adafruit.com/adafruit-circuit-playground-express/playground-sound-meter
def soundreactive():
    # read the microphone
    mic.record(samples, len(samples))

    magnitude = normalized_rms(samples)
    # You might want to print this to see the values.
    # print(magnitude)

    # Compute scaled logarithmic reading in the range 0 to NUM_PIXELS
    c = log_scale(constrain(magnitude, input_floor, input_ceiling),
                  input_floor, input_ceiling, 0, NUM_PIXELS)

    # Light up pixels that are below the scaled and interpolated magnitude.
    pixels.fill(0)
    for i in range(NUM_PIXELS):
        if i < c:
            pixels[i] = volume_color(i)
        # Light up the peak pixel and animate it slowly dropping.
        if c >= peak:
            peak = min(c, NUM_PIXELS - 1)
        elif peak > 0:
            peak = peak - 1
        if peak > 0:
            pixels[int(peak)] = PEAK_COLOR
    pixels.show()




######### Main loop

# Loop forever
while True:
    leftButtonPressed = leftButton.value
    rightButtonPressed = rightButton.value

    # left button cycles through modes
    if leftButtonPressed:
        pixels.clear() # TODO
        ledMode += 1 # increment led mode
        time.show(0.3)

        if ledMode >= NUM_MODES:
            ledMode = 0

    
    # right button controls brightness
    if rightButtonPressed:
        brightness += brightness_int
        time.show(0.3)
        if brightness > max_brightness:
            brightness = min_brightness



    # set led mode
    if ledMode == 0:
        pallete = RainbowColors_p
        rainbow()
    elif ledMode == 1:
        pallete = OceanColors_p
        rainbow()
    elif ledMode == 2:
        pallete = LavaColors_p
        rainbow()
    elif ledMode == 3:
        pallete = ForestColors_p
        rainbow()
    elif ledMode == 4:
        pallete = PartyColors_p
        rainbow()
    elif ledMode == 5:
        soundreactive()
    else:
        pixels.clear()
# end loop












#