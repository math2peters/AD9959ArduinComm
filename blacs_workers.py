#####################################################################
#                                                                   #
# Copyright 2019, Monash University and contributors                #
#                                                                   #
# This file is part of labscript_devices, in the labscript suite    #
# (see http://labscriptsuite.org), and is licensed under the        #
# Simplified BSD License. See the license.txt file in the root of   #
# the project for the full license.                                 #
#                                                                   #
#####################################################################

from collections import defaultdict
import time

import labscript_utils.h5_lock  # Must be imported before importing h5py.
import h5py
import numpy as np
from labscript.labscript import set_passed_properties


from blacs.tab_base_classes import Worker


class AD9959ArduinoCommWorker(Worker):

    def init (self):
        # Once off device initialisation code called when the
        # worker process is first started .
        # Usually this is used to create the connection to the
        # device and/or instantiate the API from the device
        # manufacturer

        global serial; import serial

        # mappings between commands sent to arduino and their meaning
        self.command_dict = {"freq":1, "phase":2, 'ramp':3, 'amplitude':4}
        
        # start up the serial connection
        self.connection = serial.Serial(self.com_port, baudrate=self.baud_rate, timeout=0.1)

        # system clock period in Hz: 20 MHz clock + 20x frequency double = 400 MHz clock 
        # the extra factor of 4 accounts for the fact that 4 bytes need to be transferred (I think)
        # see https://www.analog.com/media/en/technical-documentation/data-sheets/ad9959.pdf page 25
        self.sys_clock = 1/(400e6 / 4)
        
        time.sleep(0.3)
        # implement default values
        for key in self.default_values:
            channel = self.channel_mappings[key]
            channel_int = int(channel[-1])
            frequency = self.default_values[key]
            freq_list = [frequency]
            print("Setting Default {}: {:2.3E}".format(key, frequency))
            # program it into the arduino
            self.set_frequency(channel_int, freq_list)
            
    
    def set_frequency(self, channel, freq_list):
        """Command the arduino to set the frequency of the specified DDS channel

        Args:
            channel (int): The channel to set
            freq_list ([int list]): The list of frequencies to set in Hz
            
        """
        # div_32 bool: for the MOT and Repump locks, the AD4007 divides the actual frequency by 32
        if self.div_32:
            freq_list = [n / 32.0 for n in freq_list]
        # number of frequencies to write
        self.connection.write(channel.to_bytes(1, 'big'))
        self.connection.write(self.command_dict['freq'].to_bytes(1, 'big'))
        self.connection.write(len(freq_list).to_bytes(1, 'big'))
        
        # convert each frequency into a byte array 4 bytes long, then send each 
        # sequentially. 
        for freq in freq_list:
            freq = int(freq) 
            byte_array = freq.to_bytes(4, 'big')
            for by in byte_array:
                self.connection.write(by.to_bytes(1, 'big'))

    def set_phase(self, channel, phase):
        """Command the arduino to set the phase of the specified DDS channel

        Args:
            channel (int): The channel to set
            phase (int): The phase (in degrees) to send to the DDS
        """

        # The Phase register is 14 bits long in the DDS, so convert a degree into bits to send to arduino
        phase_int = int((phase%360) / 360.0 * 2**14)
        num_phases = 1
        # number of frequencies to write
        self.connection.write(channel.to_bytes(1, 'big'))
        self.connection.write(self.command_dict['phase'].to_bytes(1, 'big'))
        self.connection.write(num_phases.to_bytes(1, 'big'))

        # convert each into a byte array 2 bytes long, then send each 
        # sequentially.
        byte_array = phase_int.to_bytes(2, 'big')
        for by in byte_array:
            self.connection.write(by.to_bytes(1, 'big'))

    def set_ramp(self, channel, ramp_start, ramp_stop, ramp_time_up, ramp_time_down, clock_cycles_per_increment=1):
        """Tell the AD9959 to ramp

        Args:
            channel (int): the channel to ramp
            ramp_start (int): the frequency in Hz to start the ramp at
            ramp_stop (int): see above
            ramp_time_up (float): the time to ramp up in (s)
            ramp_time_down (float): see above
            clock_cycles_per_increment (int, optional): How many clock cycles occur every time the DDS steps up the frequency
            For example, if set to 255 and the ramp up rate is 1 Hz / s, the DDS will step the frequency by 1 Hz every 255 clock cycles
            There are some subtleties with how quickly the DDS can actually change the frequency if set to one, since it reads in 4 bytes which requires
            4 clock cycles if this parameter is set to 1 . Defaults to 1.
        """

        # The change in frequency between the beginning and end of the ramp
        delta_frequency = abs(ramp_stop - ramp_start)
        # The rate at which to ramp in Hz / s
        ramp_rate_up = delta_frequency / ramp_time_up
        ramp_rate_down = delta_frequency / ramp_time_down

        # If the user asks us to ramp more slowly than one Hz per clock cycle, we can change the the DDS to instead increment the frequency once every 255 
        # clock cycles for the maximally slow rate
        # the four accounts for the fact that we no longer need to worry about the byte loading time since this is no longer limiting how quickly we change freq.
        if ramp_rate_up < 1 / self.sys_clock or ramp_rate_down < 1 / self.sys_clock:
            clock_cycles_between_increment = 255 * 4

        # ramp_rate_up in Hz / clock cycle = ramp_rate_up in Hz / s * clock_cycles_per_increment * sys_clock period (s) per cycle
        ramp_rate_up = ramp_rate_up * clock_cycles_per_increment * self.sys_clock
        ramp_rate_down = ramp_rate_down * clock_cycles_per_increment * self.sys_clock

        # if the rate is too slow, we change the DDS to instead increment the frequency every 255 clock cycles
        if ramp_rate_up < 1:
            print(f"Ramp rate up {ramp_rate_up} too slow, rounding up to 1")
            ramp_rate_up = max(ramp_rate_up, 1)
        if ramp_rate_down < 1:
            print(f"Ramp rate down {ramp_rate_down} to slow, rounding up to 1")
            ramp_rate_down = max(ramp_rate_down, 1)

        ramp_rate_up = int(ramp_rate_up)
        ramp_rate_down = int(ramp_rate_down)

        self.connection.write(channel.to_bytes(1, 'big'))
        self.connection.write(self.command_dict['ramp'].to_bytes(1, 'big'))
        self.connection.write(int(0).to_bytes(1, 'big'))

        self.connection.write(ramp_start.to_bytes(4, 'big'))
        self.connection.write(ramp_stop.to_bytes(4, 'big'))
        self.connection.write(ramp_rate_up.to_bytes(4, 'big'))
        self.connection.write(clock_cycles_per_increment.to_bytes(4, 'big'))
        self.connection.write(ramp_rate_down.to_bytes(4, 'big'))
        self.connection.write(clock_cycles_per_increment.to_bytes(4, 'big'))

    def set_amplitude(self, channel, amplitude):
        """Command the arduino to set the phase of the specified DDS channel

        Args:
            channel (int): The channel to set
            phase (double): The amplitude (between 0 and 1) to set. The maximimal value in bits for the amplitude is 1024
        """

        # The Phase register is 14 bits long in the DDS, so convert a degree into bits to send to arduino
        amp_int = int(amplitude*1023)

        self.connection.write(channel.to_bytes(1, 'big'))
        self.connection.write(self.command_dict['amplitude'].to_bytes(1, 'big'))
        # write only one amplitude
        self.connection.write(int(1).to_bytes(1, 'big'))

        # convert each into a byte array 2 bytes long, then send each 
        # sequentially.
        byte_array = amp_int.to_bytes(2, 'big')
        for by in byte_array:
            self.connection.write(by.to_bytes(1, 'big'))


    def shutdown ( self ):
        # Once off device shutdown code called when the
        # BLACS exits
        self.connection.close()

    def program_manual ( self , front_panel_values ):
        # Update the output state of each channel using the values
        # in front_panel_values ( which takes the form of a
        # dictionary keyed by the channel names specified in the
        # BLACS GUI configuration
        # return a dictionary of coerced / quantised values for each
        # channel , keyed by the channel name (or an empty dictionary )
        return {}
    def transition_to_buffered ( self , device_name , h5_file_path,
    initial_values , fresh ):
        # Access the HDF5 file specified and program the table of
        # hardware instructions for this device .
        # Place the device in a state ready to receive a hardware
        # trigger (or software trigger for the master pseudoclock )
        #
        # The current front panel state is also passed in as
        # initial_values so that the device can ensure output
        # continuity up to the trigger .
        #
        # The fresh keyword indicates whether the entire table of
        # instructions should be reprogrammed (if the device supports
        # smart programming )
        # Return a dictionary , keyed by the channel names , of the
        # final output state of the shot file . This ensures BLACS can
        # maintain output continuity when we return to manual mode
        # after the shot completes .

        # self.h5_filepath = h5_file
        # self.device_name = device_name

        # From the H5 sequence file, get the sequence we want programmed into the arduino
        with h5py.File(h5_file_path, 'r') as hdf5_file:
            
            devices = hdf5_file['devices'][device_name]

            for channel in devices.keys():
                print("Setting Frequency for {}".format(channel))

                if "frequency" in channel:
                    # extract the integer part of the name
                    channel_int = int(channel[-1])
                    freq_list = list(devices[channel])
                    print(list(freq_list))
                    # program it into the arduino
                    self.set_frequency(channel_int, freq_list)

                if "phase" in channel:
                    print("Setting Phase for {}".format(channel))
                    channel_int = int(channel[-1])
                    # unpack the list
                    phase = devices[channel][0]
                    print("Phase {} deg".format(phase))
                    self.set_phase(channel_int, phase)

                if "amplitude" in channel:
                    print("Setting Amplitude for {}".format(channel))
                    channel_int = int(channel[-1])
                    # unpack the list
                    amplitude = devices[channel][0]
                    print("Amplitude {} fraction (0-1)".format(amplitude))
                    self.set_amplitude(channel_int, amplitude)

                # give the arduino time to implement the changes
                time.sleep(1e-4)

        final_values = {}
        return final_values


    def transition_to_manual ( self ):
        # Called when the shot has finished , the device should
        # be placed back into manual mode
        # return True on success
        return True

    def abort_transition_to_buffered ( self ):
        # Called only if transition_to_buffered succeeded and the
        # shot if aborted prior to the initial trigger
        # return True on success
        return True
    def abort_buffered ( self ):
        # Called if the shot is to be abort in the middle of
        # the execution of the shot ( after the initial trigger )
        # return True on success
        return True

