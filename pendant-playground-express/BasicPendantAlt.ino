// Demo program for testing library and board - flip the switch to turn on/off buzzer

#include <Adafruit_CircuitPlayground.h>

// we light one pixel at a time, this is our counter
int pix1 = 0;
int pix2 = 0;
int pix3 = 0;
int pix4 = 0;

void setup() {

  CircuitPlayground.begin();

  // turn off speaker when not in use
  CircuitPlayground.speaker.enable(false);
  for (int ln = 0; ln < 11; ln++) {
   CircuitPlayground.setPixelColor(ln, CircuitPlayground.colorWheel(25));
  }
 }

    
void loop() {

   for (int ln = 0; ln < 5; ln++) {
   pix1=ln;
   pix2=ln+5;
   pix3=ln-1;
   pix4=ln+4;
   if (pix2==10) { pix2=0;}
   if (pix3==-1) { pix3=9;}
  
   CircuitPlayground.setPixelColor(pix1, CircuitPlayground.colorWheel(150));
   CircuitPlayground.setPixelColor(pix2, CircuitPlayground.colorWheel(150));
   CircuitPlayground.setPixelColor(pix3, CircuitPlayground.colorWheel(25));
   CircuitPlayground.setPixelColor(pix4, CircuitPlayground.colorWheel(25)); 
   delay(100);
    }
 }
