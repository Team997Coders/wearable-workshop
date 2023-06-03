import board
import neopixel
import time
from math import fmod

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.1)

def getRGB (numbercode):
  r = 0
  g = 0
  b = 0
  self_numbercode = fmod(numbercode, 764)
  if self_numbercode <= 255:
    r = 255 - self_numbercode
    g = self_numbercode
    b = 0
  if self_numbercode > 255 and self_numbercode <= 510:
    r = 0
    g = 510 - self_numbercode
    b = self_numbercode - 255
  if self_numbercode > 510 and self_numbercode < 765:
    r = self_numbercode - 510
    g = 0
    b = 765 - self_numbercode
  return [r, g, b]

i = 0

while True:
  for i in range(0, 765, 15):
    for j in range(10):
      code = i + (j * 76)
      rgb = getRGB(code)
      pixels[j] = (rgb[0], rgb[1], rgb[2])
  time.sleep(0.01)