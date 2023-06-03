# Light up name badge!

In this project we are going to show off the pybadger with a few different editable screens.
*This project requires the Adafruit pybadger. A pygamer may also work, but may need modifications and has not been tested.*

## Instructions:

1. Install the circuit python runtime for the pybadger (IMPORTANT, make sure you use this link as it's different for the pybadger rather than the circuit playground express)
    1. First download the circuit python runtime, version 8.x stable [CircuitPython runtime](https://circuitpython.org/board/pybadge/)
    2. Extract the files by right clicking and pressing extract here.
    3. Press the reset button in the center of the playground express twice quickly. The LEDs will turn green and your computer should recognize a new USB drive called CPLAYBOOT.
    4. Drag the .uf2 file you downloaded and extracted into the CPLAYBOOT drive. The board should flash then reboot.
    5. If your board reboots and shows up as a USB media called CIRCUITPY then you have done it correctly!
2. Download the code repository [here](https://github.com/Team997Coders/wearable-workshop)
    1. Click on *code* on the top right of the screen and select *Download ZIP*.
    2. Navigate to your downloads folder and extract the ZIP file.
    3. Navigate to the newly created folder and find light-up-badge/src/code.py file.
3. Install the needed libraries on the pyabdger. (Possibly done for you)
    1. Copy the all of the folders and files in wearable-workshop/light-up-badge/lib/ to the CIRCUITPY drive to be in /lib/.
3. Download code to the pybadger
    1. Turn off the pybadger
    2. Plug in the pybadger using the USB cable into your computer. This should show up as a USB flashdrive.
    3. Navigate to the USB flashdrive file folder.
    3. Copy the light-up-badge/src/code.py file onto the flashdrive. You will need to overwrite the previous code.py.
    4. The pybadger after a few second should start running the new code.py!
4. Let's change the name from *Inigo Montoya* to your name.
    1. Find the code.py on the pybadger (flashdrive) and open it using the carot editor.
    2. Find the line that sets what name is displayed (hint it's line 15!)
    3. Modify the line to show your name instead! Make sure to put your name between single qoutes like this ```name = 'Ian'```
    4. Save the file to see if the changes worked.
5. What else can we try?
    1. Change the scrolling message to something new.
    2. Fix the background on the buisness card screen.
        1. Need to copy over the ```chsrobotics.bmp``` file as well as the code.py file.
        2. Make your own '.bmp' file and show it as the background to the buisness card.
    3. There is a single NEOPixel on the front of the badger. Can you turn it on? CircuitPython [NeoPixel Guide](https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel)
    4. Try getting a "Stage" game running on your pybadge using these instruction [Stage game library](https://learn.adafruit.com/circuitpython-stage-game-library/overview)
    5. *Experts only* Try making your own "Stage" game!

### Needed libraries

* adafruit bitmap_font
* adafruit_bus_device
* adafruit display_shapes
* adafruit_display_text
* adafruit_pybadger
* adafruit_lis3dh.mpy
* neopixel.mpy
