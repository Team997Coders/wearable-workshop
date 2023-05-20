#include <Adafruit_CircuitPlayground.h>
#include <FastLED.h>

// tell FastLEED all about the Circuit Playground's layout

#define CP_PIN     8   //circuit playground's neopixels live on pin 17
#define NUM_LEDS      10   // number of neopixels on the circuit playground
#define COLOR_ORDER GRB

// The right button will control the neopxiels' brightness.  Use these 
// varables to control how many brightness levels you'd like.

uint8_t brightness = 30;  // initial brightness level
uint8_t minbrightness = 10;  // minimum brightness level
uint8_t maxbrightness = 180;  //maximum brightness level -- can be set as high as 255
uint8_t brightnessint = 40;  //amount of brightness added for each button press.  

int STEPS = 10;  //makes the rainbow colors more or less spread out
int NUM_MODES = 5;  // change this number if you add or subtract modes

CRGB leds[NUM_LEDS];      // set up an LED array

CRGBPalette16 currentPalette;
TBlendType    currentBlending;

int ledMode = 0;       //Initial mode 
bool leftButtonPressed;
bool rightButtonPressed;

// SOUND REACTIVE SETUP --------------
// based on Adafruit's VU Meter code: https://learn.adafruit.com/led-ampli-tie/overview?view=all#the-code

#define MIC_PIN         A4                                    // Analog port for microphone
#define DC_OFFSET  0                                          // DC offset in mic signal - if unusure, leave 0
                                                              // I calculated this value by serialprintln lots of mic values
#define NOISE     200                                         // Noise/hum/interference in mic signal and increased value until it went quiet
#define SAMPLES   60                                          // Length of buffer for dynamic level adjustment
#define TOP (NUM_LEDS + 2)                                    // Allow dot to go slightly off scale
#define PEAK_FALL 10                                          // Rate of peak falling dot
 
byte
  peak      = 0,                                              // Used for falling dot
  dotCount  = 0,                                              // Frame counter for delaying dot-falling speed
  volCount  = 0;                                              // Frame counter for storing past volume data
int
  vol[SAMPLES],                                               // Collection of prior volume samples
  lvl       = 10,                                             // Current audio level, change this number to adjust sensitivity
  minLvlAvg = 0,                                              // For dynamic adjustment of graph low & high
  maxLvlAvg = 512;


// SETUP -----------------------------------------------------
void setup() {
  Serial.begin(57600);
  CircuitPlayground.begin();
  FastLED.addLeds<WS2812B, CP_PIN, COLOR_ORDER>(leds, 10).setCorrection( TypicalLEDStrip );
  currentBlending = LINEARBLEND;
  set_max_power_in_volts_and_milliamps(5, 500);               // FastLED 2.1 Power management set at 5V, 500mA

  
}

void loop()  {

  leftButtonPressed = CircuitPlayground.leftButton();
  rightButtonPressed = CircuitPlayground.rightButton();

  if (leftButtonPressed) {  //left button cycles through modes
    clearpixels(); 
    ledMode=ledMode+1;
    delay(300);
    if (ledMode > NUM_MODES){
    ledMode=0;
     }
  }
   if (rightButtonPressed) {   // brightness control button
     brightness = brightness + brightnessint;
     delay(300);
     if (brightness > maxbrightness) {
      brightness=minbrightness;
     }
     
   }
  
 switch (ledMode) {
       case 0: currentPalette = RainbowColors_p; rainbow(); break;
       case 1: currentPalette = OceanColors_p; rainbow(); break;                    
       case 2: currentPalette = LavaColors_p; rainbow(); break;   
       case 3: currentPalette = ForestColors_p; rainbow(); break;
       case 4: currentPalette = PartyColors_p; rainbow(); break;
       case 5: soundreactive(); break; 
       case 99: clearpixels(); break;
       
}
}
void clearpixels()
{
  CircuitPlayground.clearPixels();
   for( int i = 0; i < NUM_LEDS; i++) {
   leds[i]= CRGB::Black;
    }
   FastLED.show();
}

void rainbow()
{
  
  static uint8_t startIndex = 0;
  startIndex = startIndex + 1; /* motion speed */

  FillLEDsFromPaletteColors( startIndex);

  FastLED.show();
  FastLED.delay(20);}

//this bit is in every palette mode, needs to be in there just once
void FillLEDsFromPaletteColors( uint8_t colorIndex)
{ 
  for( int i = 0; i < NUM_LEDS; i++) {
    leds[i] = ColorFromPalette( currentPalette, colorIndex, brightness, currentBlending);
    colorIndex += STEPS;
  }
}


void soundreactive() {

  uint8_t  i;
  uint16_t minLvl, maxLvl;
  int      n, height;
   
  n = analogRead(MIC_PIN);                                    // Raw reading from mic
  n = abs(n - 512 - DC_OFFSET);                               // Center on zero
  
  n = (n <= NOISE) ? 0 : (n - NOISE);                         // Remove noise/hum
  lvl = ((lvl * 7) + n) >> 3;                                 // "Dampened" reading (else looks twitchy)
 
  // Calculate bar height based on dynamic min/max levels (fixed point):
  height = TOP * (lvl - minLvlAvg) / (long)(maxLvlAvg - minLvlAvg);
 
  if (height < 0L)       height = 0;                          // Clip output
  else if (height > TOP) height = TOP;
  if (height > peak)     peak   = height;                     // Keep 'peak' dot at top
 
 
  // Color pixels based on rainbow gradient
  for (i=0; i<NUM_LEDS; i++) {
    if (i >= height)   leds[i].setRGB( 0, 0,0);
    else leds[i] = CHSV(map(i,0,NUM_LEDS-1,20,70), 255, 255);  //constrained to yellow color, change CHSV values for rainbow
  }
 
  // Draw peak dot  -- circuit playground
  if (peak > 0 && peak <= NUM_LEDS-1) leds[peak] = CHSV(map(peak,0,NUM_LEDS-1,20,70), 255, 255);

// Every few frames, make the peak pixel drop by 1:
 
    if (++dotCount >= PEAK_FALL) {                            // fall rate 
      if(peak > 0) peak--;
      dotCount = 0;
    }
  
  vol[volCount] = n;                                          // Save sample for dynamic leveling
  if (++volCount >= SAMPLES) volCount = 0;                    // Advance/rollover sample counter
 
  // Get volume range of prior frames
  minLvl = maxLvl = vol[0];
  for (i=1; i<SAMPLES; i++) {
    if (vol[i] < minLvl)      minLvl = vol[i];
    else if (vol[i] > maxLvl) maxLvl = vol[i];
  }
  // minLvl and maxLvl indicate the volume range over prior frames, used
  // for vertically scaling the output graph (so it looks interesting
  // regardless of volume level).  If they're too close together though
  // (e.g. at very low volume levels) the graph becomes super coarse
  // and 'jumpy'...so keep some minimum distance between them (this
  // also lets the graph go to zero when no sound is playing):
  if((maxLvl - minLvl) < TOP) maxLvl = minLvl + TOP;
  minLvlAvg = (minLvlAvg * 63 + minLvl) >> 6;                 // Dampen min/max levels
  maxLvlAvg = (maxLvlAvg * 63 + maxLvl) >> 6;                 // (fake rolling average)


show_at_max_brightness_for_power();                         // Power managed FastLED display
  Serial.println(LEDS.getFPS()); 
}
