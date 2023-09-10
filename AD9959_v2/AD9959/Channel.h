
#ifndef _Channel_H_
#define _Channel_H_

#include "Arduino.h"
#include "AD9959.h"

class Channel
{
public:
  long freq_list[100];
  // the length of the above live (not all 100 elements need be filled)
  int num_elements_channel;
  // the index of the frequency list that the DDS is currently outputting for the ch
  int reset_state_channel;
  // these are telling us that we should wait to reset things until we have a full on/off cycle from the trigger
  int counter_channel; 
  int step_channel;
  
  int register_channel;
  // whether or not to step to the next frequency
  int reset_pin;
  // whether or not to reset the counter
  int step_pin;
	Channel(int, int, int);

  void setFreqList(int, long [100], AD9959);
  void setPhase(double, AD9959);
  void setAmplitude(int, AD9959);
  void checkStep(AD9959);
  void checkReset(AD9959);

};

#endif
