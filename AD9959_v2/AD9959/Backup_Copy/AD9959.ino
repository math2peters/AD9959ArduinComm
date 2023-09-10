/*
 * Revised Code by Aditya 6/23/21 - Matthew Peters
 */

#include <SPI.h>
#include "AD9959.h"
#include "Communication.h"

//Construct objectives
comSerial arduino;
/*
    Pin 10 is SS pin of Arduino Uno. Select pin 8 and 9 as IOUpdate and reset.
    Pin 7, 6, 5, 4 are for Profile 0 (p0), p1, p2, p3, respectively.
*/
AD9959 DDS(10, 50, 22, 7, 6, 5, 4);

//Channels on the DDS, the corresponding channel must be enabled to see an output on that channel
int CH[4]   = {0x10, 0x20, 0x40, 0x80}; // CH[0]: MOT, CH[1]: repump+

// Define the frequencies that we will be stepping through when the trigger is set to high
long freq_MOT[20] = {0}; 
long freq_repump[20] = {0}; 

// The lengths of the above lists
byte num_elements = 0;
byte num_elements_MOT = 0;
byte num_elements_repump = 0;

int flag = 0; // flag = 1: MOT, flag = 2: repump

// the index of the frequency list that the DDS is currently outputting for the MOT channel
int counter_MOT = 0; 
// whether or not to step to the next frequency
int step_MOT = 0;
// whether or not to reset the counter
int reset_state_MOT = 0;

// same as above but for repump
int counter_repump = 0;
int step_repump = 0;
int reset_state_repump = 0;

// input pins for stepping/resetting: the reset pin does not need to be used.
int step_MOT_pin = 30;
int reset_ch_MOT = 31;
int step_repump_pin = 40;
int reset_ch_repump = 41;

void setup() 
{
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(step_MOT_pin, INPUT);
    pinMode(reset_ch_MOT, INPUT);
    pinMode(step_repump_pin, INPUT);
    pinMode(reset_ch_repump, INPUT);
//  Normal begin and warming up of Serial port.
    Serial.begin(115200);
    while(!Serial) ;

//  Start SPI
//  In initialize(), set the External REF frequency.
    SPI.begin();
    DDS.initialize(20000000);   
}

void loop() {
  
if (Serial.available() > 1){  
    flag = Serial.read();

    if (flag == 1){
      num_elements_MOT = Serial.read();
      num_elements = num_elements_MOT;
  
    }


    if (flag == 2){
      num_elements_repump = Serial.read();
      num_elements = num_elements_repump;

    }

    
    for (byte a = 0; a<num_elements; a+= 1){
      while(Serial.available()<3){
        1+1;
      }
      float temp1 = Serial.read();
      float temp2 = Serial.read();
      float temp3 = Serial.read();
      if(flag == 1) { freq_MOT[a] = (temp1*65536 + temp2*256 + temp3)*1000; }
      if(flag == 2) { freq_repump[a] = (temp1*65536 + temp2*256 + temp3)*1000; }
    
    }  
    if(flag == 1) { 
      DDS.selectChannel(CH[0]); 
      DDS.setFreq(freq_MOT[0]);
      counter_MOT = 0;
    }
    if(flag == 2) { 
      DDS.selectChannel(CH[3]); 
      DDS.setFreq(freq_repump[0]);
      counter_repump = 0;
      }  
}  

/*----------------------------------------------------*/
/*---------------------MOT control--------------------*/
/*----------------------------------------------------*/

if (digitalRead(step_MOT_pin) == LOW){
  step_MOT = 0;
}
if (digitalRead(step_MOT_pin) == HIGH && step_MOT == 0){
  step_MOT = 1;
    

  if (counter_MOT < num_elements_MOT){
    DDS.selectChannel(CH[0]);
    DDS.setFreq(freq_MOT[counter_MOT]);
    counter_MOT += 1;
  }  
}

if (digitalRead(reset_ch_MOT) == LOW){
  reset_state_MOT = 0;
}

if(digitalRead(reset_ch_MOT) == HIGH && reset_state_MOT == 0){
  
  DDS.selectChannel(CH[0]);
  DDS.setFreq(freq_MOT[0]);
  counter_MOT = 0;
  reset_state_MOT = 1;
}

/*----------------------------------------------------*/
/*-------------------repump control-------------------*/
/*----------------------------------------------------*/

if (digitalRead(step_repump_pin) == LOW){
  step_repump = 0;
}
if (digitalRead(step_repump_pin) == HIGH && step_repump == 0){
  step_repump = 1;
  if (counter_repump < num_elements_repump){
    DDS.selectChannel(CH[3]);
    DDS.setFreq(freq_repump[counter_repump]);
    counter_repump += 1;
  }
}

if (digitalRead(reset_ch_repump) == LOW){
  reset_state_repump = 0;
}
if(digitalRead(reset_ch_repump) == HIGH && reset_state_repump == 0){
  DDS.selectChannel(CH[3]);
  DDS.setFreq(freq_repump[0]);
  counter_repump = 0;
  reset_state_repump = 1;
}
}
