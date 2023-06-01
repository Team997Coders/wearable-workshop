# wearable-workshop
Code for the 2023 CHS wearable workshop. This Readme has the basic instruction for installing


# Getting Started
The circuit playground express and Gemma are neat little programmable boards from Adafruit. It is particularly designed to make it easy to design, make, and program wearable electronic projects. We are planning on using the CircuitPython environment to program these boards. For more information on documentation for using the Circuit Playground Express check out this Adafruit link: https://learn.adafruit.com/adafruit-circuit-playground-express

## Download and Install CircuitPython (This step has already been done for you)


1. First download the circuit python runtime, version 8.x [CircuitPython runtime](https://circuitpython.org/board/circuitplayground_express/)
2. Extract the files by right clicking and pressing extract here.
3. Press the reset button in the center of the playground express twice quickly. The LEDs will turn green and your computer should recognize a new USB drive called CPLAYBOOT.
4. Drag the .uf2 file you downloaded and extracted into the CPLAYBOOT drive. The board should flash then reboot.
5. If your board reboots and shows up as a USB media called CIRCUITPY then you have done it correctly!

For more info see this [link](https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-quickstart).

If you are running Windows 7 or older, you may need to follow the instructions:
[Windows Driver installation](https://learn.adafruit.com/adafruit-circuit-playground-express/adafruit2-windows-driver-installation)


## Download and Install the circuit python libraries (This step may have been done for you)

Download and install the needed adafruit libraries (version 8.x) [CircuitPython libraries](https://circuitpython.org/libraries) Then move the required libraries into the /lib/ folder on the CIRCUITPY drive.

## Plugging in the circuit playground express / Gemma
Use the USB cable to plug the device into your computer. The playground express / Gemma will show up as a USB drive to your computer.

## Using the web code editor

1. Find and connect to the editor.
    1. Navigate to the [editor](https://code.circuitpython.org/) using Google Chrome.
    2. Select USB. This should show a page about selecting a serial port and root file.
    3. Click on select serial port, there will be several options, pick the one with Circuit Playground Express in the name.
    4. Select the root folder. This should be the top of the CIRCUITPY drive. You should see the code.py file grayed out then press open to select that folder. (this may not be neccesary if you have already selected the root folder before)
    5. There may be an additional step where you click using CIRCUITPY.
2. Make code changes using the editor.
3. Click save and run to have the circuit playground express start running the changes you made.
4. Click on serial monitor to see debug messages from the circuit playground express.



# CircuitPython

CircuitPython is a slightly modified lightweight version of the python programming langauge for small electronics. For all sorts of more information about CircuitPython checkout this link [CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython).

For just the CircuitPython essentialy and documentation of functions see this link [CircuitPython Essentials](https://learn.adafruit.com/circuitpython-essentials/circuitpython-essentials)
* CircuitPython [NeoPixel Guide](https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel)



## Install an Editor (Only for information if desired)
We need to be able to edit code on the Circuit Playground Express, which needs a code editor. Skip to the relevant documentation for a Windows/Mac/Linux machine versus a Chromebook
**For expert users**: Feel free to use your favorite editor, but it won’t have built-in support for getting debug statements.

### Installing the Editor on Chromebooks
We will need to install two programs to run the editor on chromebooks. 
Caret Editor extension for Chrome https://chrome.google.com/webstore/detail/caret/fljalecfjciodhpcledpamjachpmelml?hl=en
Beagle Term https://chrome.google.com/webstore/detail/beagle-term/gkdofhllgfohlddimiiildbgoggdpoea?hl=en

The first allows us to edit files on the chromebook, the second lets us connect and see print statements.

### Installing the Editor on Mac/Windows/Linux (Skip unless you are using Mac/Windows/Linux)
Checkout adafruit's documentation directly https://learn.adafruit.com/using-circuit-playground-express-makecode-circuitpython-on-a-chromebook/using-circuitpython


