# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board

from adafruit_pybadger import pybadger
import terminalio
from adafruit_display_text.scrolling_label import ScrollingLabel

pybadger.show_badge(
    name_string="Inigio Montoya", hello_scale=2, my_name_is_scale=2, name_scale=1
)

text = "You killed my father, prepare to die...        "
my_scrolling_label = ScrollingLabel(
    terminalio.FONT, text=text, max_characters=24, animate_time=0.3, background_color=0xFFAA00)

my_scrolling_label.x = 10
my_scrolling_label.y = 10

while True:
    pybadger.auto_dim_display(
        delay=10
    )  # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        pybadger.show_business_card(
            image_name="chsrobotics.bmp",
            name_string="Inigo Montoya",
            name_scale=2,
            email_string_one="Text",
            email_string_two="Look! More text.",
            font_color=0x0000ff
        )
    elif pybadger.button.b:
        pybadger.show_qr_code(data="https://www.chsrobotics.org/")
    elif pybadger.button.start:
        pybadger.show_badge(
            name_string="Inigio Montoya", hello_scale=2, my_name_is_scale=2, name_scale=1
        )
    elif pybadger.button.select:
        board.DISPLAY.show(my_scrolling_label)
    my_scrolling_label.update()
