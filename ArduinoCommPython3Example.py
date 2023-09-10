import serial
import time

def write_freq(freq_list, flag = 0):
    """
    write the frequency you choose into the arduino, which then writes it to the DDS
    Bytes have to be written sequentially (not all at once) because of the way aditya wrote the arduino code
    The byte sequence is: 1 byte for the flag, 1 byte for the number of frequencies, and finally, 3*number of frequency bytes
    :param freq: in KHz
    :param num_freqs: number of frequencies to write, to be iterated when arduino voltage stepped
    :param flag: which output to change
    :return: void
    """
    command = 1
    ser.write(flag.to_bytes(1, 'big'))
    ser.write(command.to_bytes(1, 'big'))
    ser.write(len(freq_list).to_bytes(1, 'big'))

    for freq in freq_list:
        byte_array = freq.to_bytes(4, 'big')
        print(byte_array)
        for by in byte_array:
            ser.write(by.to_bytes(1, 'big'))

def write_phase(phase, flag = 0, num_elements=1):

    phase_int = int(phase / 360.0 * 2**14)
    command = 2
    print(phase_int)
    ser.write(flag.to_bytes(1, 'big'))
    ser.write(command.to_bytes(1, 'big'))
    ser.write(num_elements.to_bytes(1, 'big'))

    byte_array = phase_int.to_bytes(2, 'big')
    for by in byte_array:
        ser.write(by.to_bytes(1, 'big'))

def write_ramp(start, stop, delta_up, rate_up, delta_down, rate_down, flag = 0, num_elements=1):
    command = 3
    ser.write(flag.to_bytes(1, 'big'))
    ser.write(command.to_bytes(1, 'big'))
    ser.write(len([1]).to_bytes(1, 'big'))

    ser.write(start.to_bytes(4, 'big'))
    ser.write(stop.to_bytes(4, 'big'))
    ser.write(delta_up.to_bytes(4, 'big'))
    ser.write(rate_up.to_bytes(4, 'big'))
    ser.write(delta_down.to_bytes(4, 'big'))
    ser.write(rate_down.to_bytes(4, 'big'))

# This is the com port your arduino is on
port = 'COM3'

ser = serial.Serial(port, 115200, timeout=1)
# time.sleep(1)
#
# #
# write_freq([int(1e6), int(2e6), int(3e6), int(4e6)], flag=0)
# write_freq([int(1e6), int(2e6), int(3e6), int(4e6), int(5e6)], flag=1)

# time.sleep(1)
# write_ramp(int(100e6), int(200e6), 1, 1, 1, 1)
time.sleep(3)
write_freq([int(35.5e6), int(36e6)], flag=0)
# write_freq([5e6], flag=1)
#
# time.sleep(1)
# write_phase(0, flag=0)
# write_phase(0, flag=1)
#
# time.sleep(3)
# write_phase(90, flag=1)
#
# time.sleep(3)
# write_phase(180, flag=1)
#
# time.sleep(3)
# write_phase(270, flag=1)

#print(ser.readline())
while (t:= ser.readline()) != b'':
   print(t)
[print(by.to_bytes(1, 'big')) for by in ser.readline()]



ser.close()
