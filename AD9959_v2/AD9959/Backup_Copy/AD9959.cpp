#include "Arduino.h"
#include "AD9959.h"
#include <SPI.h>

//Registers
//Control Register
int CSR   = 0x00;
int FR1   = 0x01;
int FR2   = 0x02;
//Channel Register
int CFR   = 0x03;
int CFTW0 = 0x04;
int CPOW0 = 0x05;
int ACR   = 0x06;
int LSRR  = 0x07;
int RDW   = 0x08;
int FDW   = 0x09;
//Profile Register
//For Modulation and Linear Sweep
int CW1   = 0x0A;
int CW2   = 0x0B;
int CW3   = 0x0C;
int CW4   = 0x0D;
int CW5   = 0x0E;
int CW6   = 0x0F;
int CW7   = 0x10;
int CW8   = 0x11;
int CW9   = 0x12;
int CW10  = 0x13;
int CW11  = 0x14;
int CW12  = 0x15;
int CW13  = 0x16;
int CW14  = 0x17;
int CW15  = 0x18;

//Constructor
AD9959::AD9959(int CS, int IOUpdate, int reset, int p0, int p1, int p2, int p3)
{
//Initialize variables
	_CS = CS;
	_IOUpdate = IOUpdate;
	_reset = reset;
	_p[0] = p0;
	_p[1] = p1;
	_p[2] = p3;
	_p[3] = p3;

	RESOLUTION_F = 4294967296.0;
	RESOLUTION_P = 16384.0;
	_sysClk = 500000000;

	_statusCFR[0] = 0x00;
	_statusCFR[1] = 0x03;
	_statusCFR[2] = 0x02;
 

//Define pinModes
/*
	Here only additional pins are defined. MOSI, MISO, SCLK pins are pre-defined by SPI.h. 
	CS pin is basically the SS pin in SPI.h

	When CS(SS) is set to be HIGH, it ignores the master.
	A High-Low cycle of IOUpdate pin is required after a set of communication. 
	This will enable the data in register. It could be sent after each cycle or after several cycles.
*/
	pinMode(_CS, OUTPUT);
	pinMode(_IOUpdate, OUTPUT);
	pinMode(_reset, OUTPUT);
	pinMode(_p[0], OUTPUT);
	pinMode(_p[1], OUTPUT);
	pinMode(_p[2], OUTPUT);
	pinMode(_p[3], OUTPUT);

	digitalWrite(_CS, HIGH);//When the SS pin is
	digitalWrite(_IOUpdate, LOW);
	digitalWrite(_reset, LOW);//Maybe I do not need it.
	digitalWrite(_p[0], LOW);//Otherwise the Linear Sweep Mode would be turned on.
	digitalWrite(_p[1], LOW);
	digitalWrite(_p[2], LOW);
	digitalWrite(_p[3], LOW);
}

//Public function
void AD9959::initialize(unsigned long sysClk)
{
  reset();
  _sysClk = sysClk;
  setPLL_VCO(20, 1);
}

void AD9959::setPLL_VCO(byte ratio, bool enable)
{
	if(ratio > 20)
		ratio = 20;
	byte setValue = (enable << 7) + (ratio << 2);
	byte buffer[3] = {setValue, 0x00, 0x00};
	_sysClk *= ratio;
	_statusFR1 = buffer[0];
	writeReg(FR1, buffer, 3);
	IOUpdate();
}

void AD9959::reset()
{
	digitalWrite(_reset, HIGH);
	delay(10);
	digitalWrite(_reset, LOW);
}

void AD9959::IOUpdate()
{
	digitalWrite(_IOUpdate, HIGH);
	digitalWrite(_IOUpdate, LOW);
}

/*
	General remarks about all SET functions:
	Setting is active for enabled channel(s). 
	As a result, before setting up, a selectChannel function is to be called.
	This would disable other channel.
	Thus after setting we need to call SET functions four times and finally 
	choose the channels we want.
*/
void AD9959::selectChannel(byte ch)
{
	//To remain the last three bits of CSR status
 	_statusCSR = ch | (0x07 & _statusCSR);
	writeReg(CSR, _statusCSR);
}

void AD9959::setFreq(unsigned long freq)
{
	//setFrequency
	_freq = freq;
	unsigned long FTW = (unsigned long) freq * RESOLUTION_F / _sysClk;
	byte buffer[4] = {(byte)(FTW >> 24), (byte)(FTW >> 16), (byte)(FTW >> 8), (byte)FTW};
	writeReg(CFTW0, buffer, 4);
	IOUpdate();
}

void AD9959::setPhase(double phase)
{
	//Select channel(s)
//	selectChannel(ch);
	//setPhase
	_phase = phase;
	//According to datasheet, the 14bit phase accumulator require such a resolution.
	unsigned long POW = (unsigned long) RESOLUTION_P * phase / 360.0;
	byte buffer[2] = {(byte)(POW >> 8), (byte)POW};
	writeReg(CPOW0, buffer, 2);
	//IOUpdate();
}

/*
	Amplitude is controlled with a 10bit register. Maximal value is 1024.
	This actually has 24bits in total.
	The 13th bit is better to be set high for safety.
	The 14th bit should be set low.
*/
void AD9959::setAmp(unsigned long amp)
{
//	unsigned long ATW = (unsigned long) amp;
	byte buffer[3] = {0x00, (0x10 | (byte)(amp >> 8)), (byte)amp};
	writeReg(ACR, buffer, 3);
	IOUpdate();
}

unsigned long AD9959::getFreq()
{
	return _freq;
}

double AD9959::getPhase()
{
	return _phase;
}

/*
	sFTW means start frequency tuning word.
	eFTW means end frequency tuning word.
	rDW means rising delta word.
	fDW means falling delta word.
*/
void AD9959::linearSweepF(unsigned long* inputLW)
{
	unsigned long sFTW = (unsigned long) inputLW[0] * RESOLUTION_F / _sysClk;
	unsigned long eFTW = (unsigned long) inputLW[1] * RESOLUTION_F / _sysClk;
	unsigned long rDW = (unsigned long) inputLW[2] * RESOLUTION_F / _sysClk;
	unsigned long fDW = (unsigned long) inputLW[4] * RESOLUTION_F / _sysClk;

	byte bufferCFR[3] = {0x80, 0x43, 0x00};
	byte buffersFTW[4] = {(byte)(sFTW >> 24), (byte)(sFTW >> 16), (byte)(sFTW >> 8), (byte)(sFTW)};
	byte buffereFTW[4] = {(byte)(eFTW >> 24), (byte)(eFTW >> 16), (byte)(eFTW >> 8), (byte)(eFTW)};
	byte bufferRDW[4] = {(byte)(rDW >> 24), (byte)(rDW >> 16), (byte)(rDW >> 8), (byte)(rDW)};
	byte bufferFDW[4] = {(byte)(fDW >> 24), (byte)(fDW >> 16), (byte)(fDW >> 8), (byte)(fDW)};
	byte bufferLSRR[2] = {inputLW[5], inputLW[3]};
  
	writeReg(CFR, bufferCFR, 3);
	writeReg(CFTW0, buffersFTW, 4);
	writeReg(CW1, buffereFTW, 4);
	writeReg(RDW, bufferRDW, 4);
	writeReg(FDW, bufferFDW, 4);
	writeReg(LSRR, bufferLSRR, 2);
//	delay(10);
	IOUpdate();
	startSweep(inputLW[7]);
	delay(inputLW[6]);
	stopSweep(inputLW[7]);
}

/*
	sPOW means start phase tuning word.
	ePOW means end phase tuning word.
	rDW means rising delta word.
	fDW means falling delta word.
*/

/*
	Integer Version
*/

void AD9959::linearSweepP(unsigned long* inputLW)
{
	unsigned long sPOW = (unsigned long) inputLW[0] * RESOLUTION_P / 360.0;
	unsigned long ePOW = (unsigned long) inputLW[1] * RESOLUTION_P / 360.0;
	unsigned long rDW = (unsigned long) inputLW[2] * RESOLUTION_P / 360.0;
	unsigned long fDW = (unsigned long) inputLW[4] * RESOLUTION_P / 360.0;

	byte bufferCFR[3] = {0xC0, 0x43, 0x00};
	byte buffersPOW[2] = {(byte)(sPOW >> 8), (byte)(sPOW)};
/*
	Care should be taken here
	The upper 14bit will be used. So we need to make sure the way we used to contruct a byte is to set 0 at the end.
*/
	byte bufferePOW[4] = {(byte)(ePOW >> 6), (byte)(ePOW << 2), 0x00, 0x00};
	byte bufferRDW[4] = {(byte)(rDW >> 6), (byte)(rDW << 2), 0x00, 0x00};
	byte bufferFDW[4] = {(byte)(fDW >> 6), (byte)(fDW << 2), 0x00, 0x00};
	byte bufferLSRR[2] = {inputLW[5], inputLW[3]};
  
	writeReg(CFR, bufferCFR, 3);
	writeReg(CPOW0, buffersPOW, 2);
	writeReg(CW1, bufferePOW, 4);
	writeReg(RDW, bufferRDW, 4);
	writeReg(FDW, bufferFDW, 4);
	writeReg(LSRR, bufferLSRR, 2);
	IOUpdate();
	startSweep((unsigned long)inputLW[7]);
	delay((unsigned long)inputLW[6]);
	stopSweep((unsigned long)inputLW[7]);
}

/*
	Double Version
*/
void AD9959::linearSweepP(double* inputLW)
{
	unsigned long sPOW = (unsigned long) inputLW[0] * RESOLUTION_P / 360.0;
	unsigned long ePOW = (unsigned long) inputLW[1] * RESOLUTION_P / 360.0;
	unsigned long rDW = (unsigned long) inputLW[2] * RESOLUTION_P / 360.0;
	unsigned long fDW = (unsigned long) inputLW[4] * RESOLUTION_P / 360.0;

	byte bufferCFR[3] = {0xC0, 0x43, 0x00};
	byte buffersPOW[2] = {(byte)(sPOW >> 8), (byte)(sPOW)};
/*
	Care should be taken here
	The upper 14bit will be used. So we need to make sure the way we used to contruct a byte is to set 0 at the end.
*/
	byte bufferePOW[4] = {(byte)(ePOW >> 6), (byte)(ePOW << 2), 0x00, 0x00};
	byte bufferRDW[4] = {(byte)(rDW >> 6), (byte)(rDW << 2), 0x00, 0x00};
	byte bufferFDW[4] = {(byte)(fDW >> 6), (byte)(fDW << 2), 0x00, 0x00};
	byte bufferLSRR[2] = {inputLW[5], inputLW[3]};

	writeReg(CFR, bufferCFR, 3);
	writeReg(CPOW0, buffersPOW, 2);
	writeReg(CW1, bufferePOW, 4);
	writeReg(RDW, bufferRDW, 4);
	writeReg(FDW, bufferFDW, 4);
	writeReg(LSRR, bufferLSRR, 2);
	IOUpdate();
	startSweep((unsigned long)inputLW[7]);
	delay((unsigned long)inputLW[6]);
	stopSweep((unsigned long)inputLW[7]);
}

/*
	sACR means start amplitude tuning word.
	eACR means end amplitude tuning word.
	rDW means rising delta word.
	fDW means falling delta word.
*/
void AD9959::linearSweepA(unsigned long* inputLW)
{
	byte bufferCFR[3] = {0x40, 0x43, 0x00};
	byte buffersACR[3] = {0x00, (0x10 | (byte)(inputLW[0] >> 8)), (byte)(inputLW[0])};
	byte buffereACR[4] = {(byte)(inputLW[1] >> 2), (byte)(inputLW[1] << 8), 0x00, 0x00};
	byte bufferRDW[4] = {(byte)(inputLW[2] >> 2), (byte)(inputLW[2] << 8), 0x00, 0x00};
	byte bufferFDW[4] = {(byte)(inputLW[4] >> 2), (byte)(inputLW[4] << 8), 0x00, 0x00};
	byte bufferLSRR[2] = {inputLW[5], inputLW[3]};

	writeReg(CFR, bufferCFR, 3);
	writeReg(ACR, buffersACR, 3);
	writeReg(CW1, buffereACR, 4);
	writeReg(RDW, bufferRDW, 4);
	writeReg(FDW, bufferFDW, 4);
	writeReg(LSRR, bufferLSRR, 2);
//	delay(10);
	IOUpdate();
	startSweep(inputLW[7]);
	delay(inputLW[6]);
	stopSweep(inputLW[7]);
}

void AD9959::startSweep(byte ch)
{
	digitalWrite(_p[ch], HIGH);
}

void AD9959::stopSweep(byte ch)
{
	digitalWrite(_p[ch], LOW);
}

// These functions aren't used, but could be used.
void AD9959::powerDown(byte ch)
{
	selectChannel(ch);
	byte buffer[3] = {0x00, 0x03, 0xC0};
	writeReg(CFR, buffer, 3);
	IOUpdate();
}

void AD9959::setSine(byte ch)
{
	selectChannel(ch);
	byte buffer[3] = {0x00, 0x03, 0x01};
	writeReg(CFR, buffer, 3);
	IOUpdate();
}

//Private function
void AD9959::writeReg(byte infoReg, byte dataReg)
{
	SPI.beginTransaction(SPISettings(20000000, MSBFIRST, SPI_MODE0));
	SPI.transfer(infoReg);
	SPI.transfer(dataReg);
	SPI.endTransaction();
}

void AD9959::writeReg(byte infoReg, byte *dataReg, byte len)
{
  
	SPI.beginTransaction(SPISettings(20000000, MSBFIRST, SPI_MODE0));
  digitalWrite(_CS, LOW);
	SPI.transfer(infoReg);
	int i = 0;
	for(i = 0; i < len; ++i)
		SPI.transfer(dataReg[i]);
	SPI.endTransaction();
}
