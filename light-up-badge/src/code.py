# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Modified by Ian

# import the needed board information
import board

# import pybadger specific libraries
from adafruit_pybadger import pybadger
from adafruit_display_text.scrolling_label import ScrollingLabel

#
import terminalio

name = 'Inigo Montoya' # Defines the name on every screen


# By default show the My name is screen:
pybadger.show_badge(
    name_string=name, hello_scale=2, my_name_is_scale=2, name_scale=1
)

# Define the scrolling text on the scrolling label screen
text = "You killed my father, prepare to die...        "
my_scrolling_label = ScrollingLabel(
    terminalio.FONT, text=text, max_characters=24, animate_time=0.3, background_color=0xFFAA00)

# defines the scrolling label location
'''
      +x
  ┌────────►
  │┼─────────────────────┐
+y││(0,0)                │
  ││                     │
  ▼│                     │
   │                     │
   │       Pybadger      │
   │       Screen        │
   │                     │
   │                     │
   │                     │
   │                     │
   └─────────────────────┘
'''
my_scrolling_label.x = 10
my_scrolling_label.y = 10


# Loop forever
while True:

    # if button a is pressed, show the "buisness card" image
    if pybadger.button.a:
        pybadger.show_business_card(
            image_name="chsrobotics.bmp",           # change this line for the background image.
            name_string=name,            # changes the name shown on the badge
            name_scale=2,                           # size of the name shown on the badge
            email_string_one="Text",                # Text below the name
            email_string_two="Look! More text.",    # Second line of text below the name
            font_color=0x0000ff                     # font color
        )
    # If button b is pressed, show the qr code page.
    elif pybadger.button.b:
        pybadger.show_qr_code(data="https://www.chsrobotics.org/")
    # if the start button is pressed, show the default 'hello my name is' badge
    elif pybadger.button.start:
        pybadger.show_badge(
            name_string=name, hello_scale=2, my_name_is_scale=2, name_scale=1
        )
    # if select button is pressed, show the scrolling display badge.
    elif pybadger.button.select:
        board.DISPLAY.show(my_scrolling_label)
    # end if elses
    
    # the scrolling label needs to constantly be updated. perform this update no 
    # matter which screen is currently being shown.
    my_scrolling_label.update()
