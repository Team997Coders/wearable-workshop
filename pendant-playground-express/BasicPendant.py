# BasicPendant.py
# Translated to python by Ian, Arduino code written by Tom Saska.
#
#

# Import the needed libraries
import time
import board
import digitalio
from rainbowio import colorwheel
import adafruit_fancyled.fastled_helpers as helper
import neopixel


NUM_LEDS = 10
brightness = 30.0/255.0 # initial brightness
min_brightness = 10.0/255.0
max_brightness = 180/255.0
brightness_int = 40.0/255.0

steps = 10 # makes the rainbow colors more or less spread out
NUM_MODES = 6 # change this number if you add or subtract modes

# setup the neopixel strip
pixels = neopixel.NeoPixel(board.NEOPIXEL, NUM_LEDS, brightness=0.2, auto_write=False)

# setup the needed buttons
leftButton = digitalio.DigitalInOut(board.BUTTON_A)
leftButton.switch_to_input(pull=digitalio.Pull.DOWN)
rightButton = digitalio.DigitalInOut(board.BUTTON_B)
rightButton.switch_to_input(pull=digitalio.Pull.DOWN)

# initial mode
ledMode = 0
leftButtonPressed = False # button pressed
rightButtonPressed = False

# initial location
startIndex = 0
pallete = None

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

## TODO


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
    # go through each pixels and set the color
    for i in range(NUM_LEDS):
        pixels[i] = helper.ColorFromPalette(palette, colorIndex, brightness, blend)


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
    else:
        pixels.clear()
# end loop












#