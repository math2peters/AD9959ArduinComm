/* Communication.h */
#ifndef _Communication_H_
#define _Communication_H_

#include "Arduino.h"

class comSerial
{
public:
	comSerial();
	byte scan();
	
	unsigned long inte;//For setting numbers, such as frequency.
	double floa;//For setting numbers, such as phase. 
//	char* str;//For grammer detection
  char ch; //For grammer detection
private:
	byte buffer[10];
	byte flag;//flag = 3, 2, 1, 0 denotes inte, floa, str, ch, respectively.
};

#endif
