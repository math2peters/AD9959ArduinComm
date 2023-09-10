#include "Arduino.h"
#include "AD9959.h"
#include "Channel.h"
#include <SPI.h>

// list of frequencies to be set on the DDS
long freq_list[100] = {0};
// the length of the above live (not all 100 elements need be filled)
int num_elements_channel;
// the index of the frequency list that the DDS is currently outputting for the ch
int reset_state_channel = 0;
// these are telling us that we should wait to reset things until we have a full on/off cycle from the trigger
int counter_channel = 0; 
int step_channel = 0;

int register_channel;
// whether or not to step to the next frequency
int reset_pin;
// whether or not to reset the counter
int step_pin;


Channel::Channel(int reg, int step_pin_set, int reset_pin_set)
{  
  register_channel = reg;
  // whether or not to step to the next frequency
  reset_pin = reset_pin_set;
  // whether or not to reset the counter
  step_pin = step_pin_set;
  
}

void Channel::setFreqList(int num_elements, long elements[100], AD9959 DDS)
{ 
  for (int i = 0; i<num_elements; i+= 1){
    freq_list[i] = elements[i];
  }
  counter_channel = 0;
  num_elements_channel = num_elements;
  DDS.selectChannel(register_channel);
  DDS.setFreq(freq_list[0]);
}

void Channel::setPhase(double phase, AD9959 DDS)
{ 
  double RESOLUTION_P = 16384.0; // 2^14
  phase = phase / RESOLUTION_P * 360.0;
  DDS.selectChannel(register_channel);
  DDS.setPhase(phase);
}


void Channel::setAmplitude(int amplitude, AD9959 DDS)
{ 
  DDS.selectChannel(register_channel);
  DDS.setAmp(amplitude);
}
void Channel::checkStep(AD9959 DDS){

  if (digitalRead(step_pin) == LOW){
    step_channel = 0;
  }
  if (digitalRead(step_pin) == HIGH && step_channel == 0){
    step_channel = 1;
      
    if (counter_channel < num_elements_channel - 1){
      counter_channel += 1;
      DDS.selectChannel(register_channel);
      DDS.setFreq(freq_list[counter_channel]);
    }  
  DDS.IOUpdate();
//    else{
//      counter_channel = 0;
//      DDS.selectChannel(register_channel);
//      DDS.setFreq(freq_list[counter_channel]);
//    }
  }
}

void Channel::checkReset(AD9959 DDS){
  if (digitalRead(reset_pin) == LOW){
    reset_state_channel = 0;
  }
  
  if(digitalRead(reset_pin) == HIGH && reset_state_channel == 0){
    
    DDS.selectChannel(register_channel);
    DDS.setFreq(freq_list[0]);
    counter_channel = 0;
    reset_state_channel = 1;
  
    DDS.IOUpdate();
  }

}
