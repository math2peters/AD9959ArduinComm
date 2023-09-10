/*AD9959.h*/
/*
	Achieved Functions:
	1. Set Frequency.
	2. Set Phase.
	3. Set Amplitude.
	4. Serial Control.
	5. Linear Sweep.
	6. Power down control.
	Comtemporarily we could not read the value of a register, to reduce the wires needed for operation.
	However, because all the value we set could be directly seen, that would not be a problem.
	
	Modulation Function could be directly modified from Linear Sweep Function. They are essentially similar. 
	But for modulation requires more parameters which could only be determined by user, I leave it out.
*/
#ifndef _AD9959_H_
#define _AD9959_H_

#include "Arduino.h"

class AD9959
{
public:
	AD9959(int, int, int, int, int, int, int);

//	General Functions
	void initialize(unsigned long);
	void reset();
	void IOUpdate();
	void powerDown(byte);

//	Setting-Up Functions
	void setFreq(unsigned long);
	void setPhase(double);
	void setAmp(unsigned long);
	void setSine(byte);
	void selectChannel(byte);
	void setPLL_VCO(byte, bool);
	unsigned long getFreq();
	double getPhase();

//	Linear Sweep Function
//	void linearSweepF(unsigned long, unsigned long, unsigned long, byte, unsigned long, byte);
	void linearSweepF(unsigned long* inputLW);
//	void linearSweepP(double, double, double, byte, double, byte);
	void linearSweepP(double* inputLW);
	void linearSweepP(unsigned long* inputLW);
//  void linearSweepP(unsigned long, unsigned long, unsigned long, byte, unsigned long, byte);
//	void linearSweepA(unsigned long, unsigned long, unsigned long, byte, unsigned long, byte);
	void linearSweepA(unsigned long* inputLW);
	void startSweep(byte);
	void stopSweep(byte);	

private:
	void writeReg(byte, byte);
	void writeReg(byte, byte *, byte);

	int _CS, _IOUpdate, _reset;
	int _p[4];
	byte _statusCSR, _statusFR1;
	byte _statusCFR[3];
	unsigned long _sysClk, _freq;
	double RESOLUTION_F, RESOLUTION_P, _phase;
};

#endif
