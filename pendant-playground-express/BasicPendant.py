# BasicPendant.py
# Translated to python by Ian, Arduino code written by Tom Saska.
#
#

# Import the needed libraries
import time
import board
import digitalio
from rainbowio import colorwheel
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

# Sound reactive setup
# Based on Adafruit VU meter code

## TODO

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
        #currentPalette = RainbowColors_p
        rainbow()
    else:
        pixels.clear()
# end loop



# rainbow function
def rainbow():
    global startIndex
    startIndex += 1 # this sets the motion speed.

    FillLEDsFromPaletteColors(startIndex)

    pixels.show()
    time.show(0.02)

def FillLEDsFromPaletteColors(colorIndex):










#