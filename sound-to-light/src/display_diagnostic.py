import time
import neopixel
from display_settings import DisplaySettings

def ShowLightOrder(pixels: neopixel.NeoPixel, settings: DisplaySettings, delay: float = None):
    '''
    Turn the pixels on in order by index number
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

def ShowRowColumnOrder(pixels: neopixel.NeoPixel, settings: DisplaySettings, delay: float = None):
    '''
    Light each row (0 to N), then each column (0 to M) This is useful to
    determine if a pixel indexer is addressing the display as intended
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
