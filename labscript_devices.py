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

from labscript import IntermediateDevice, AnalogOut, DigitalOut, Trigger
from labscript.labscript import Device, set_passed_properties
import numpy as np

class AD9959ArduinoComm ( IntermediateDevice ):

    # A human readable name for device model used in error messages
    description = "AD9959-Arduino Comm"
    # The labscript Output classes this device supports
    allowed_children = [ ]
    # The maximum update rate of this device (in Hz)
    clock_limit = 1e4

    @set_passed_properties(
        property_names={
            'connection_table_properties':
                [
                    'name',
                    'com_port',
                    'channel_mappings',
                    'baud_rate',
                    'channels',
                    'div_32',
                    'default_values'
                ]
        }
    )
    def __init__ ( self , name , com_port, channel_mappings, trigger_mappings, div_32=False, default_values={}, channels=['ch0', 'ch1', 'ch2', 'ch3'], baud_rate = 115200, **kwargs):
        """ initialize device

        Args:
            name (str): name of device
            com_port (int): the comport the device is attached to 
            baud_rate (int, optional): The baud rate (rate of communication over serial). Defaults to 115200.
            trigger_mappings (dict): A dictionary of triggers that maps the trigger for that channel to the channel name.
            default_values (dict): default values for the channels. Ex: {"MOT":1250e6}
            channel_mappings  (str, optional): the names of the channel. Example: {"MOT":"ch1", "Repump":"ch2"}.
            div_32 (bool): For the MOT and Repump frequencies, we divide them by 32 because of the frequency rescaling done by the AD4007
        """
        IntermediateDevice.__init__ ( self , name , parent_device=None)
        self.BLACS_connection = "ArduinoDDS {}, BAUD: {}".format( com_port , str( baud_rate ) )
        self.name = name
        self.default_values = default_values
        self.trigger_mappings = trigger_mappings
        self.channels = channels
        # define list of frequencies to set for each AD9959 channel
        self.freq_dict = {}
        for channel in self.channels:
            self.freq_dict[channel] = []
        self.phase_dict = {}
        # the default phase between channels should be 0
        for channel in self.channels:
            self.phase_dict[channel] = 0
        self.amplitude_dict = {}
        # the default amplitude for channels is 0.5
        for channel in self.channels:
            self.amplitude_dict[channel] = 0.5

        self.min_trigger_pulse_width = 250e-6
        self.div_32 = div_32

        # upper and lower lims of the DDS frequency
        self.lower_lim = .01e6 # Hz
        self.upper_lim = 400e6 # Hz
        
        if div_32:
            self.lower_lim = .01*32e6 # Hz
            self.upper_lim = 400*32e6 # Hz

        self.channel_mappings  = channel_mappings

    def generate_code(self,hdf5_file):
        """Write the frequency sequence for each channel to the HDF file

        Args:
            hdf5_file (hdf): labscript hdf file
        """

        Device.generate_code(self, hdf5_file)

        for channel_num, channel in enumerate(self.freq_dict.keys()):
            
            cur_freq_list = self.freq_dict[channel]

            # check to see if any frequencies are set for the channel
            if len(cur_freq_list) > 0:

                # see if they fit in the limits; correct them if they do not
                if not self.check_frequency(cur_freq_list):
                    cur_freq_list = self.coerce_frequency(cur_freq_list)

                grp = hdf5_file.require_group(f'/devices/{self.name}/')
                
                # reserve space for channel to set
                dset_freq = grp.require_dataset('frequency_{}'.format(channel),
                (len(cur_freq_list),),dtype='f')
                # list the channel mappings
                # S30 means string with 30 characters (in UTF-8)
                dset_str = grp.require_dataset('channel_mappings', (len(self.channel_mappings),),dtype='S30')

                dset_freq[:] = cur_freq_list
                dset_str[:] = [n.encode("ascii", "ignore") for n in self.channel_mappings ]

                dset_phase = grp.require_dataset('phase_{}'.format(channel),
                (1,),dtype='f')
                dset_phase[0] = self.coerce_phase(self.phase_dict[channel])

                dset_amplitude = grp.require_dataset('amplitude_{}'.format(channel),
                (1,),dtype='f')
                dset_amplitude[0] = self.coerce_amplitude(self.amplitude_dict[channel])

    def check_frequency(self, freq_list):
        """ check whether or not the frequencies are within the limits required
        by the DDS

        Args:
            freq_list ([float]): list of frequencies to step to

        Returns:
            [bool]: whether or not the the frequencies fit within the required lims
        """

        if max(freq_list) > self.upper_lim or min(freq_list) < self.lower_lim:
            print("Frequencies were clipped to match the limits: 0-200 MHz")
            return False
        else:
            return True

    def coerce_frequency(self, freq_list):
        """Change the frequency if it is 

        Args:
            freq_list ([float]): see above  

        Returns:
            [float]: the coerced list
        """
        print("Warning: Frequencies input into DDS {} are not within limits".format(self.name))
        return list(np.clip(freq_list, self.lower_lim, self.upper_lim))

    def program_freq(self, channel_descriptor, freq_list):
        """set the frequencies in the dictionary, which will be used in the 
        generate code method

        Args:

            freq_list : see above
        """

        self.freq_dict[self.channel_mappings[channel_descriptor]] = freq_list

    def jump_frequency(self, t, channel_descriptor, frequency, trigger=True):
        """Jump the AD9959 frequency to the next value. The first time it is set, trigger should be set to false

        Args:
            t (float): time at which to trigger in seconds
            channel_descriptor (string): the channel to set
            frequency (float): frequency to set
            trigger (bool, optional): Whether or not to trigger. Defaults to True.
        """

        self.freq_dict[self.channel_mappings[channel_descriptor]].append(frequency)
        if trigger:
            #print("Triggering {} at t={}".format(channel_descriptor, t))
            self.trigger_mappings[channel_descriptor].trigger_next_freq(t)
   


    def coerce_phase(self, phase):
        
        if not 0 <= phase < 360:
            phase = min(max(0, phase), 360)
            print("Warning: Phases into DDS {} should be between 0 and 360 deg".format(self.name))
        return phase

    def program_phase(self, channel_descriptor, phase):
        """set the phases in the dictionary, which will be used in the 
        generate code method

        Args:

            phase: the phase to send to the arduino channel
        """

        self.phase_dict[self.channel_mappings[channel_descriptor]] = phase

    def coerce_amplitude(self, amplitude):

        if not 0 < amplitude < 1:
            amplitude = min(max(0, amplitude), 1)
            print("Warning: Amplitudes into DDS {} should be between 0 and 1".format(self.name))
        return amplitude

    def program_amplitude(self, channel_descriptor, amplitude):
        """set the phases in the dictionary, which will be used in the 
        generate code method

        Args:

            phase: the phase to send to the arduino channel
        """

        self.amplitude_dict[self.channel_mappings[channel_descriptor]] = amplitude

class AD9959ArduinoTriggerAnalog(AnalogOut, Trigger):
    """Class to trigger the arduino to move to the next frequency using an analog output

    """

    def __init__ ( self , name , parent_device, connection, default_value=0,**kwargs):
        AnalogOut.__init__ ( self , name=name , connection=connection, parent_device=parent_device, default_value=default_value )

        self.limits = (0, 3)
        self.min_trigger_pulse_width = 100e-6 # the trigger (high + low time) must be at least this long or the arduino may not register it
        self.prev_trigger_time = -1
        self.times_triggered = 0

    def trigger(self, trigger_time):
        """Trigger the next frequency

        Args:
            channel_name ([type]): [description]
            trigger_time (float): time to trigger

        Raises:
            Exception: if the trigger time is too close to the previously set trigger time

        Returns:
            float: length of the trigger
        """

        if abs(trigger_time- self.prev_trigger_time) < self.min_trigger_pulse_width:
            raise Exception("Invalid triggering sequence. Please ensure the times between triggers are larger than the minimum.")

        self.prev_trigger_time = trigger_time
        self.constant(trigger_time,3.3)
        self.constant(trigger_time+self.min_trigger_pulse_width/2,0)

        self.times_triggered += 1

        return self.min_trigger_pulse_width


class AD9959ArduinoTriggerDigital(DigitalOut):
    """Class to trigger the arduino to move to the next frequency using digital output

    """

    def __init__ ( self , name , parent_device, connection, default_value=0,**kwargs):
        DigitalOut.__init__ ( self , name=name , connection=connection, parent_device=parent_device, default_value=default_value )
        
        self.min_trigger_pulse_width = 250e-6 # the trigger (high + low time) must be at least this long or the arduino may not register it
        self.prev_trigger_time = -1
        self.times_triggered = 0

    def trigger_next_freq(self, trigger_time):
        """Trigger the next frequency

        Args:
            channel_name ([type]): [description]
            trigger_time (float): time to trigger

        Raises:
            Exception: if the trigger time is too close to the previously set trigger time

        Returns:
            float: length of the trigger
        """

        if abs(trigger_time- self.prev_trigger_time) < self.min_trigger_pulse_width:
            raise Exception("Invalid triggering sequence. Please ensure the times between triggers are larger than the minimum.")

        # if self.times_triggered > num_frequencies:
        #     raise Exception("Invalid triggering sequence. Please ensure you do not trigger the arduino more times than the number of frequencies you set minus 1")
        self.prev_trigger_time = trigger_time

        self.prev_trigger_time = trigger_time
        self.go_high(trigger_time)
        self.go_low(trigger_time+self.min_trigger_pulse_width/2)

        return self.min_trigger_pulse_width