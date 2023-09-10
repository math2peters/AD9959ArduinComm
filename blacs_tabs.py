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



from blacs.device_base_class import DeviceTab, define_state
from matplotlib.pyplot import text
from qtutils.qt.QtCore import*
from qtutils.qt.QtGui import *
from qtutils.qt.QtWidgets import *
from PyQt5.QtWidgets import QComboBox, QGridLayout, QLineEdit

class AD9959ArduinoCommTab(DeviceTab):
    def initialise_GUI ( self ):
        """Initializes the GUI tab for the arduino/dds communication
        """
        
        # pull the layout of the tab so that we can place widgets in it
        layout = self.get_tab_layout()

        # Get properties from connection table.
        device = self.settings['connection_table'].find_by_name(
            self.device_name
        )
        
        self.com_port = device.properties['com_port']
        self.baud_rate = device.properties['baud_rate']
        self.channels = device.properties['channels']
        self.channel_mappings = device.properties['channel_mappings']
        self.div_32 = device.properties['div_32']
        self.default_values = device.properties['default_values']

        # Here we add ramping functionality to ramp the frequency of a channel linearly
        ramp_row = QGridLayout()

        self.ramp_channel_label = QLabel()
        self.ramp_channel_label.setText("Ramp Channel")
        ramp_row.addWidget(self.ramp_channel_label, 0, 0)
        self.ramp_channel_combobox = QComboBox()
        for channel in self.channel_mappings:
            self.ramp_channel_combobox.addItem(channel)
        ramp_row.addWidget(self.ramp_channel_combobox, 0, 1)
        self.ramp_start_label = QLabel()
        self.ramp_start_label.setText("Ramp Start (Hz)")
        ramp_row.addWidget(self.ramp_start_label, 0, 2)
        self.ramp_start_textbox = QLineEdit()
        ramp_row.addWidget(self.ramp_start_textbox, 0, 3)
        self.ramp_stop_label = QLabel()
        self.ramp_stop_label.setText("Ramp Stop (Hz)")
        ramp_row.addWidget(self.ramp_stop_label, 0, 4)
        self.ramp_stop_textbox = QLineEdit()
        ramp_row.addWidget(self.ramp_stop_textbox, 0, 5)
        self.ramp_time_up_label = QLabel()
        self.ramp_time_up_label.setText("Ramp Up Time (s)")
        ramp_row.addWidget(self.ramp_time_up_label, 1, 0)
        self.ramp_time_up_textbox = QLineEdit()
        ramp_row.addWidget(self.ramp_time_up_textbox, 1, 1)
        self.ramp_time_down_label = QLabel()
        self.ramp_time_down_label.setText("Ramp Down Time (s)")
        ramp_row.addWidget(self.ramp_time_down_label, 1, 2)
        self.ramp_time_down_textbox = QLineEdit()
        ramp_row.addWidget(self.ramp_time_down_textbox, 1, 3)
        self.ramp_button = QPushButton()
        self.ramp_button.setText("Ramp")
        self.ramp_button.setStyleSheet("border :1px solid black")
        ramp_row.addWidget(self.ramp_button, 1, 5)
        layout.addLayout(ramp_row)


        # various widgets we will put in the layout
        self.freq_label_widgets = {}
        self.freq_textbox_widgets = {}
        self.freq_button_widgets = {}

        self.phase_label_widgets = {}
        self.phase_textbox_widgets = {}
        self.phase_button_widgets = {}

        self.amplitude_label_widgets = {}
        self.amplitude_textbox_widgets = {}
        self.amplitude_button_widgets = {}

        for row, channel_name in enumerate(self.channel_mappings):
            # for each channel, make a new row to put the label, editable textbox, and button to send the contents of the text box to the arduino
            cur_row = QGridLayout()
            
            self.freq_label_widgets[channel_name] = QLabel()
            self.freq_label_widgets[channel_name].setText(channel_name + " Freq (Hz) Set")
            self.freq_label_widgets[channel_name].setAlignment(Qt.AlignLeft)
            #self.freq_label_widgets[channel_name].setFixedSize(150, 25)
            cur_row.addWidget(self.freq_label_widgets[channel_name], 0, 0)

            self.freq_textbox_widgets[channel_name] = QLineEdit(str(self.default_values[channel_name]))
            self.freq_textbox_widgets[channel_name].setAlignment(Qt.AlignCenter)
            #self.freq_textbox_widgets[channel_name].setFixedSize(150, 25)
            cur_row.addWidget(self.freq_textbox_widgets[channel_name], 0, 1)

            self.freq_button_widgets[channel_name] = QPushButton()
            self.freq_button_widgets[channel_name].setText("Send " + channel_name)
            #self.freq_button_widgets[channel_name].setFixedSize(150, 25)
            self.freq_button_widgets[channel_name].setStyleSheet("border :1px solid black")
            cur_row.addWidget(self.freq_button_widgets[channel_name], 0, 2)

            self.phase_label_widgets[channel_name] = QLabel()
            self.phase_label_widgets[channel_name].setText(channel_name + " Phase (deg) Set")
            self.phase_label_widgets[channel_name].setAlignment(Qt.AlignLeft)
            #self.phase_label_widgets[channel_name].setFixedSize(150, 25)
            cur_row.addWidget(self.phase_label_widgets[channel_name], 0, 3)

            self.phase_textbox_widgets[channel_name] = QLineEdit()
            self.phase_textbox_widgets[channel_name].setAlignment(Qt.AlignCenter)
            #self.phase_textbox_widgets[channel_name].setFixedSize(150, 25)
            cur_row.addWidget(self.phase_textbox_widgets[channel_name], 0, 4)

            self.phase_button_widgets[channel_name] = QPushButton()
            self.phase_button_widgets[channel_name].setText("Send " + channel_name)
            #self.phase_button_widgets[channel_name].setFixedSize(150, 25)
            self.phase_button_widgets[channel_name].setStyleSheet("border :1px solid black")
            cur_row.addWidget(self.phase_button_widgets[channel_name], 0, 5)

            self.amplitude_label_widgets[channel_name] = QLabel()
            self.amplitude_label_widgets[channel_name].setText(channel_name + " Amplitude (0-1) Set")
            self.amplitude_label_widgets[channel_name].setAlignment(Qt.AlignLeft)
            #self.amplitude_label_widgets[channel_name].setFixedSize(150, 25)
            cur_row.addWidget(self.amplitude_label_widgets[channel_name], 1, 0)

            self.amplitude_textbox_widgets[channel_name] = QLineEdit()
            self.amplitude_textbox_widgets[channel_name].setAlignment(Qt.AlignCenter)
            #self.amplitude_textbox_widgets[channel_name].setFixedSize(150, 25)
            cur_row.addWidget(self.amplitude_textbox_widgets[channel_name], 1, 1)

            self.amplitude_button_widgets[channel_name] = QPushButton()
            self.amplitude_button_widgets[channel_name].setText("Send " + channel_name)
            #self.amplitude_button_widgets[channel_name].setFixedSize(150, 25)
            self.amplitude_button_widgets[channel_name].setStyleSheet("border :1px solid black")
            cur_row.addWidget(self.amplitude_button_widgets[channel_name], 1, 2)


            layout.addLayout(cur_row)

        # we add the buttons to a button group so that we can determine which button was pressed
        self.freq_btn_grp = QButtonGroup()
        self.freq_btn_grp.setExclusive(True)
        for button in self.freq_button_widgets.values():
            self.freq_btn_grp.addButton(button)

        self.phase_btn_grp = QButtonGroup()
        self.phase_btn_grp.setExclusive(True)
        for button in self.phase_button_widgets.values():
            self.phase_btn_grp.addButton(button)

        self.amplitude_btn_grp = QButtonGroup()
        self.amplitude_btn_grp.setExclusive(True)
        for button in self.amplitude_button_widgets.values():
            self.amplitude_btn_grp.addButton(button)

        # when one of the buttons in the button group is pressed, execute on_click method (below)
        self.freq_btn_grp.buttonClicked.connect(self.freq_on_click)
        self.phase_btn_grp.buttonClicked.connect(self.phase_on_click)
        self.ramp_button.clicked.connect(self.ramp_on_click)
        self.amplitude_btn_grp.buttonClicked.connect(self.amplitude_on_click)

    MODE_MANUAL = 1
    @define_state(MODE_MANUAL,True)  
    def freq_on_click(self, btn):
        """On a button press, send the corresponding textbox contents to the arduino

        Args:
            btn ([type]): which of the buttons were pressed
        """
        self.logger.debug('entering set freq')

        # the last part of the name of the button is the channel that is being changed
        channel_name = btn.text().split(" ")[-1]

        # get the number of the channel from the name of the channel
        channel_number = int(self.channel_mappings[channel_name][-1])
        
        # try to get the float value from the textbox, check to see if the contents are a float, then set the DDS channel
        try:
            # format and split string: valid inputs are a single number, a list of numbers separated by commas
            textbox_value_split = (self.freq_textbox_widgets[channel_name].text().replace(" ", "").replace("[", "").replace("]", "")).split(',')
            
            freq_list = [float(n) for n in textbox_value_split]


            results = yield(self.queue_work('main_worker','set_frequency', channel_number, freq_list))
        except:
            self.logger.debug("PLEASE ENTER A VALID FLOAT")

        return

    @define_state(MODE_MANUAL, True)
    def phase_on_click(self, btn):
        """On a button press, send the corresponding textbox contents to the arduino

        Args:
            btn ([type]): which of the buttons were pressed
        """
        self.logger.debug('entering set phase')

        # the last part of the name of the button is the channel that is being changed
        channel_name = btn.text().split(" ")[-1]

        # get the number of the channel from the name of the channel
        channel_number = int(self.channel_mappings[channel_name][-1])

        # try to get the float value from the textbox, check to see if the contents are a float, then set the DDS channel
        try:
            textbox_value = float(self.phase_textbox_widgets[channel_name].text())

            results = yield (self.queue_work('main_worker', 'set_phase', channel_number, textbox_value))
        except:
            self.logger.debug("PLEASE ENTER A VALID FLOAT")

        return

    @define_state(MODE_MANUAL, True)
    def amplitude_on_click(self, btn):
        """On a button press, send the corresponding textbox contents to the arduino

        Args:
            btn ([type]): which of the buttons were pressed
        """
        self.logger.debug('entering set amplitude')

        # the last part of the name of the button is the channel that is being changed
        channel_name = btn.text().split(" ")[-1]

        # get the number of the channel from the name of the channel
        channel_number = int(self.channel_mappings[channel_name][-1])

        # try to get the float value from the textbox, check to see if the contents are a float, then set the DDS channel
        try:
            textbox_value = float(self.amplitude_textbox_widgets[channel_name].text())

            results = yield (self.queue_work('main_worker', 'set_amplitude', channel_number, textbox_value))
        except:
            self.logger.debug("PLEASE ENTER A VALID FLOAT")

        return

    @define_state(MODE_MANUAL, True)
    def ramp_on_click(self, btn):
        """Tell the DDS channel to ramp

        Args:
            btn (ramp_button): the button that was pressed
        """

        self.logger.debug('entering set ramp')

        # the last part of the name of the button is the channel that is being changed
        channel_name = self.ramp_channel_combobox.currentText()

    

        # try to get the value from the textbox, check to see if the contents are a numbers, then set the DDS. 
        # We must first convert from string to float, then to int, in order to allow inputs like 10e6
        try:
            channel_number = int(self.channel_mappings[channel_name][-1])
            ramp_start = int(float(self.ramp_start_textbox.text()))
            ramp_stop = int(float(self.ramp_stop_textbox.text()))
            ramp_time_up = float(self.ramp_time_up_textbox.text())
            ramp_time_down = float(self.ramp_time_down_textbox.text())

            results = yield(self.queue_work('main_worker', 'set_ramp', channel_number, ramp_start, ramp_stop, ramp_time_up, ramp_time_down))
        except ValueError:
            self.logger.debug("PLEASE ENTER A VALID FLOAT")
            print("Invalid entry")

        return

        


    def initialise_workers(self):
        connection_table = self.settings['connection_table']
        device = connection_table.find_by_name(self.device_name)

        # Create and set the primary worker
        self.create_worker(
            'main_worker',
            'user_devices.Rydberg.AD9959ArduinoComm.blacs_workers.AD9959ArduinoCommWorker',
            {
                'com_port': self.com_port,
                'baud_rate': self.baud_rate,
                'channels': self.channels,
                'channel_mappings': self.channel_mappings,
                'div_32': self.div_32,
                'default_values': self.default_values
            },
        )
        self.primary_worker = 'main_worker'

