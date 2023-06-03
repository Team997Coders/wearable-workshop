# Optional Upgrades

## Add a power switch

A feather's [batt pin is powered even when the EN pin is grounded](https://learn.adafruit.com/adafruit-feather-m0-basic-proto/power-management#enable-pin-3122388).  This means to completely turn off the device we have to add a switch to the battery cable itself.  To accomplish this, cut either the red or black wire (Your Choice!) on the battery cable.  Solder a few CM of wire on each pin of the power button.  Then solder the wires to each wire from the battery.  

Once this is done you can disable battery power with the switch.  Note that in order to charge the battery when plugged into USB power the battery switch will still need to be in the "ON" position.

## Add a mode button

There are several displays built into the source code.  Adding a button would allow us to cycle through each display each time it is pressed.  To do this, wire the button to the 3.3v Feather pin and one of the digital IO pins.  (**Not Digital IO #6!** That is used by the NeoPixel Featherwing). Note that buttons often have four pins, two pair of which are always connected.  If you do not have a multimeter to test using the pair furthest apart (diagonal) is usually a safe bet.   

Then in the code we need to add some logic to the program loop that changes the display.

