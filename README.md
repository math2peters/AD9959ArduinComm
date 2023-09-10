# Explanation

This contains the code to talk to an arduino, which in turn programs the AD9959 frequency through SPI. It is currently configured to jump our MOT and repump frequencies (which are output on channels 1 and 2 of the DDS, respectively) and control the relative phases of the microwave DDS. The arduino can update the frequency of the DDS roughly every millisecond.
The connections for the arduino to AD9959 are:

PIN7 -> P0 (This controls the ramp of frequencies, which is not currently implemented in labscript of the arduino code)

PIN50 -> IOUpdate (This is critical for actuating the values sent over SPI)

PIN22 -> Reset (This is used to reset the AD9959 to its default state -- which is called at the beginning of programming)

SPI SCK -> SLCK (The clock for SPI)

SPI MOSI -> SDIO_0 (Master out slave in -- the commands are sent to the DDS over this pin)

SPI GND -> SDIO_0_GND (connect the ground of the SPI to the ground of the SDIO_0 pin)

CSB -> Add jumper (The "Channel Select Bar" pin i.e. !(Channel Select). This tells the AD9959 that it is the one being talked to when the CSB is grounded
In theory, multiple DDSs can be controlled by the same arduino by using a different pin to "activate" the DDS you are talking to)

PWR_DWN -> Add jumper


The organization is typical of user-added labscript devices, except there is an extra folder AD9959_v2. The folder contains code which should be uploaded to the arduino.