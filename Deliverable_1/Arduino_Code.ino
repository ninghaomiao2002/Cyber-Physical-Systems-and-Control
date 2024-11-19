// include the library
#include <Joystick.h>

// define the pin connections
#define joyX A2
#define joyZ A3
#define joyThrottle A0

// initialize the variables
int xAxis_ = 0;
int zAxis_ = 0;
int throttle_ = 0;

// set up functions
Joystick_ Joystick(0x03, 0x04, 32, 2,true,false,true,false,false,false,false,true,false,false,false);
const bool initAutoSendState = true;

void setup() {
  Joystick.begin();
}

void loop() {
  Serial.begin(9600);
  
  // read joyX and re-map it
  xAxis_ = analogRead(joyX);
  xAxis_ = map(xAxis_,264,758,0,1023);

  // send data
  Joystick.setXAxis(xAxis_);
  // Serial.println(xAxis_);
  
  // read joyZ and re-map it
  zAxis_ = analogRead(joyZ);
  zAxis_ = map(zAxis_,264,758,0,1023);

  // send data
  Joystick.setZAxis(zAxis_);
  // Serial.println(zAxis_);
  
  // read joyThrottle and re-map it
  throttle_ = analogRead(joyThrottle);
  throttle_ = map(throttle_,0,1023,0,511);

  // send data
  Joystick.setThrottle(throttle_);
  // Serial.println(throttle_);
  
delay(10);
}