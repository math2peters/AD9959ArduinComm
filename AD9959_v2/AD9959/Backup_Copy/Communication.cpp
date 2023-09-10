#include "Arduino.h"
#include "Communication.h"

comSerial::comSerial()
{
	inte = 0;
	floa = 0.0;
	flag = 0;
//	ch = 'q';
}

byte comSerial::scan()
{
	int count = 0;
  inte = 0;
  floa = 0.0;
  flag = 0;
	while(Serial.available() <= 0)
		delay(50);// This is crucial to wait until all the data are transferred through serial port.
	while(Serial.available() > 0)
	  buffer[count++] = Serial.read();
//  Serial.println(count); //It seems only your input will be recorded. When the input stream is off, everything would be fine.
/*	
	Criterion: 
	1. For grammer input, the first input must be letter.
	2. For float input, comtemporarily the last but one input must be '.'.
	3. For integer input, all should be integer of course.
*/
/*
	if(buffer[0] > 64 && buffer[0] < 123)//letter and '[', ']', '\', '^', '_', '`'
	{
		ch = new char[count];
		for(int i = 0; i < count; ++i)
			ch[i] = buffer[i];
		flag = 1;
	}
*/
  if(buffer[0] > 64 && buffer[0] < 123)//letter and '[', ']', '\', '^', '_', '`'
  {
    ch = buffer[0];
    flag = 0;
  }
	else if(buffer[count - 2] == '.')
	{
		for(int i = 0; i < count - 2; ++i)
		{
			floa *= 10;
			floa += buffer[i] - 48;
		}
		floa += (buffer[count - 1] - 48) / 10.0;
		flag = 2;
	}
	else if(buffer[0] > 47 && buffer[0] < 58)
	{
		for(int i = 0; i < count; ++i)
		{
			inte *= 10;
			inte += buffer[i] - 48;
		}
		flag = 3;
	}
	else
	{
		flag = 4;
		Serial.println("Type error. Please enter again.");
	}
 // Serial.println(buffer[0]);
	return flag;
}
