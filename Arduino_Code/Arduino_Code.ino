//Arduino Joystick 2.0 Library, by MHeironimus (https://github.com/MHeironimus)
//Beginners Guide, by Daniel Cantore
//Example Code (Oct 2020), with in-depth commenting 

//Initial Definitions and Setup
//Libary Inclusion
#include <Joystick.h>

//Define and Allocate Input Pins to memorable names
#define joyX A2
#define joyZ A3
//#define joyZ A5
#define joyThrottle A0
//#define joyButton1 9åå
//#define joyButton2 8
//#define joyButton3 7

//Initializing Axis as Integers, at a 0 default value
int xAxis_ = 0;
int zAxis_ = 0;
//int zAxis_ = 0;
int throttle_ = 0;


Joystick_ Joystick(0x03, 0x04, 32, 2,true,false,true,false,false,false,false,true,false,false,false);

//Set Auto Send State
//Enables Auto Sending, allowing the controller to send information to the HID system, rather than waiting to be asked.
const bool initAutoSendState = true;

void setup() {
  Joystick.begin();
}

void loop() {
  Serial.begin(9600);
  //Axis Reading during Runtime
  //Setting Read functions for each axis and parsing correctly. The X axis will be used as an example for explanation

  //Reading the X Axis analog pin to the xAxis_ variable for processing
  xAxis_ = analogRead(joyX);
  // Serial.println(xAxis_);
  // xAxis_ = map(xAxis_,264,758,0,1023);
  xAxis_ = map(xAxis_,264,758,0,1023);
  Joystick.setXAxis(xAxis_);
  Serial.println(xAxis_);


  zAxis_ = analogRead(joyZ);
  zAxis_ = map(zAxis_,264,758,0,1023);
  Joystick.setZAxis(zAxis_);
  //Serial.println(zAxis_);

  

  throttle_ = analogRead(joyThrottle);
  // Serial.println(throttle_);
  throttle_ = map(throttle_,0,1023,0,511);
  Joystick.setThrottle(throttle_);
  //Serial.println(throttle_);
  
 
delay(10);
}