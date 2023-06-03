# https://core-electronics.com.au/guides/circuit-playground/
#   ir-controlled-lights-with-circuitpython-adafruit-circuit-playground-express-tutorial/
# IR Controlled Lights for the Adafruit Circuit Playground Express
# Written for core-electronics.com.au
# For use on two Circuit Playgrounds, pressing button A or B on one board
# turns on a short light animation on the receiving board.

from adafruit_circuitplayground.express import cpx
import board
import random
import time
import pulseio
import array

# Create IR input, maximum of 59 bits.
pulseIn = pulseio.PulseIn(board.IR_RX, maxlen=59, idle_state=True)
# Clears any artifacts
pulseIn.clear()
pulseIn.resume()

# Creates IR output pulse
pulse = pulseio.PulseOut(board.IR_TX, frequency=38000, duty_cycle=2 ** 15)

# Array for button A pulse, this is the pulse output when the button is pressed
# Inputs are compared against this same array
# array.array('H', [x]) must be used for IR pulse arrays when using pulseio
# indented to multiple lines so its easier to see
pulse_A = array.array('H', [1000, 3800, 65000, 950, 300, 200, 300, 1000, 350, 175,
    275, 215, 275, 250, 275, 215, 275, 225, 275, 215, 275, 1000, 300, 225, 275,
    950, 300, 950, 300, 1000, 300, 950, 300, 250, 275, 700, 300, 950, 300, 450,
    300, 475, 300, 215, 275, 725, 300, 950, 300, 200, 300, 715, 325, 900, 315,
    425, 315, 1000, 65000])
pulse_B = array.array('H', [1000, 3800, 65000, 960, 300, 200, 300, 950, 350, 190,
    215, 245, 300, 225, 275, 225, 275, 215, 275, 200, 300, 700, 300, 200, 300,
    700, 300, 1000, 315, 675, 300, 1000, 300, 200, 300, 700, 300, 950, 300,
    950, 300, 700, 300, 700, 300, 450, 300, 475, 275, 715, 300, 225, 275, 450,
    300, 450, 300, 1000, 65000])

# Fuzzy pulse comparison function. Fuzzyness is % error
def fuzzy_pulse_compare(pulse1, pulse2, fuzzyness=0.5):
    if len(pulse1) != len(pulse2):
        return False
    for i in range(len(pulse1)):
        threshold = int(pulse1[i] * fuzzyness)
        if abs(pulse1[i] - pulse2[i]) > threshold:
            return False
    return True

# Initializes NeoPixel ring
cpx.pixels.brightness= 0.2
cpx.pixels.fill((0, 0, 0))
cpx.pixels.show()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 85:
        return (int(pos*3), int(255 - (pos*3)), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - (pos*3)), 0, int(pos*3))
    else:
        pos -= 170
        return (0, int(pos*3), int(255 - pos*3))

# neopixel animation for random white sparkles
def sparkles(wait):  # Random sparkles - lights just one LED at a time
    i = random.randint(0, len(cpx.pixels) - 1)  # Choose random pixel
    cpx.pixels[i] = ((255, 255, 255))  # Set it to current color
    cpx.pixels.write()  # Refresh LED states
# Set same pixel to "off" color now but DON'T refresh...
# it stays on for now...bot this and the next random
# pixel will be refreshed on the next pass.
    cpx.pixels[i] = [0, 0, 0]
    time.sleep(0.008)  # 8 millisecond delay

# NeoPixel animation to create a rotating rainbow
def rainbow_cycle(wait):
    for j in range(30):
        for i in range(len(cpx.pixels)):
            idx = int((i * 256 / len(cpx.pixels)) + j*20)
            cpx.pixels[i] = wheel(idx & 255)
        cpx.pixels.show()
        time.sleep(wait)
    cpx.pixels.fill((0, 0, 0,))

# serial print once when activated
last_length = 0
print('IR Activated!')

while True:
# when button is pressed, send IR pulse
# detection is paused then cleared and resumed after a short pause
# this prevents reflected detection of own IR
    while cpx.button_a:
        print("Send Button A")
        pulseIn.pause()  # pauses IR detection
        pulse.send(pulse_A)  # sends IR pulse
        time.sleep(.2)  # wait so pulses dont run together
        pulseIn.clear()  # clear any detected pulses to remove partial artifacts
        pulseIn.resume()  # resumes IR detection
    while cpx.button_b:
        print("Send Button B")
        pulseIn.pause()
        pulse.send(pulse_B)
        time.sleep(.2)
        pulseIn.clear()
        pulseIn.resume()

# Wait for a pulse to be detected of desired length
    while len(pulseIn) >= 59:  # our array is 59 bytes so anything shorter ignore
        pulseIn.pause()
# converts pulseIn raw data into useable array
        detected = array.array('H', [pulseIn[x] for x in range(len(pulseIn))])
        print(len(pulseIn))
        print(detected)

    # Got a pulse, now compare against stored pulse_A and pulse_B
        if fuzzy_pulse_compare(pulse_A, detected):
            print('Received correct Button A control press!')
            t_end = time.monotonic() + 2  # saves time 2 seconds in the future
            while time.monotonic() < t_end: # plays sparkels until time is up
                sparkles(.001)

        if fuzzy_pulse_compare(pulse_B, detected):
            print('Received correct Button B control press!')
            t_end = time.monotonic() + 2
            while time.monotonic() < t_end:
                rainbow_cycle(.001)

        time.sleep(.1)
        pulseIn.clear()
        pulseIn.resume()

    if len(pulseIn) != last_length:
        print(len(pulseIn))
        last_length = len(pulseIn)
