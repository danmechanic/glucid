#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
glucid8824.py defines a class `Glucid8824` which
implements an api to a Lucid 8824 Analog/Digital Audio Converter
RS232 interface over a serial port.

See glucid.py for a `main` and associated functions 
that provide a useful command line tool `glucid` to configure 
the Lucid 8824/.

Copyright (C) 2017,2018  Daniel R Mechanic (dan.mechanic@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License ONLY.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

__version__ = '0.5.0a'
__author__ = 'Daniel R Mechanic (dan.mechanic@gmail.com)'
CONFIGFILE='.glucid.cfg'

import logging
import configparser
import getopt
import sys
import os
import serial
from distutils.util import strtobool
from _ast import Or

class Glucid8824:
    """The glucid8824 class represents a single Lucid
    ADA8824 unit and provides methods to communicate with
    a Lucid ADA8824 via its RS232 Serial port over the Serial
    Port of a Computer.
    """
    # hex constants:
    # sysex start & end byte
    STARTBYTE = 'f0'
    ENDBYTE = 'f7'

    # Lucid Manufacturer ID & 8824ID
    LUCIDINCID = ['00', '00', '5e']

    # Lucid 8824 Specific Model ID
    MODELID = '58'

    # Available Commands and thier
    # decimal values
    COMMANDSET = {
            'GetMode': '60',
            'SetMode': '20',
            'GetSync': '61',
            'SetSync': '21',
            'GetOptSrc': '62',
            'SetOptSrc': '22',
            'GetAnalogSrc': '63',
            'SetAnalogSrc': '23',
            'GetAesSrc': '64',
            'SetAesSrc': '24',
            'GetAnalogGain': '70',
            'SetAnalogGain': '30',
    }

    # OPTIONS FOR FRONT METER
    METER = ('Analog In', 'Digital In', 'Analog Out', 'Digital Out')

    # OPTION FOR DIGITAL IN 1/2
    DIG1 = ('AES', 'S/PDIF')

    # SYNC OPTIONS
    SYNC = (
        # 0:
        'ADAT',
        # 1:
        'WordClock',
        # 2:
        '44.1 Internal',
        # 3:
        '48 Internal',
        # 4:
        'AES In1',
        # 5:
        'AES In2',
        # 6:
        'AES In3',
        # 7:
        'S/PDIF In'
             )

    # OPTIONS FOR ANALOG OUT SRC
    ANALOG_SRC = (
        # 0:
        'ADAT In',
        # 1:
        'AES In'
             )

    # OPTIONS FOR AES DIGITAL OUT SRC
    AES_SRC = (
        #  0
        'ADAT In',
        # 1
        'Analog In'
        )

    # OPTIONS FOR ADAT OUT SRC
    OPTICAL_SRC = (
        # 0 analog input
        'Analog In',
        # 1 AES input
        'AES In'
    )

    # MIN DB LEVEL - 0
    MINIO = '00'

    # MAX DB LEVEL - 80
    MAXIO = '7f'

    # PRO (+4dBu) CONSTANTS
    # -8 dB IN
    # +1 dB OUT
    PLUS4IN = '58'
    PLUS4OUT = '61'

    # CONSUMER (-10dBV) CONSTANTS
    # +4 dB IN
    # -11 dB OUT
    MINUS10IN = '64'
    MINUS10OUT = '55'

    # Keep a dictionary of valid
    # devices to talk over, and the format
    # they use...
    # rs232 uses 9600
    # midi uses 31250

    DEVICES = {
        'rs232' : [
            '/dev/ttyUSB0',
            '/dev/tty.usbserial',
            'COM1',
            '/dev/ttyUSB1',
            '/dev/ttyUSB2',
            '/dev/ttyUSB3',
            '/dev/ttyUSB4',
            '/dev/ttyUSB5',
            '/dev/ttyS0',
            '/dev/ttyS1',
            '/dev/ttyS2',
            '/dev/ttyS3',
            '/dev/ttyS4',
            '/dev/ttyS5',
            '/dev/ttyAMA0',
            '/dev/ttyAMA1',
            '/dev/ttyACM0',
            '/dev/ttyACM1',
            '/dev/rfcomm0',
            '/dev/rfcomm1',
            '/dev/ircomm0',
            '/dev/ircomm1',
            '/dev/cuau0',
            '/dev/cuau1',
            '/dev/cuau2',
            '/dev/cuaU0',
            '/dev/cuaU1',
            'COM1',
            'COM2',
            'COM3',
            'COM4',
            '/dev/ttyUSB0',
            '/dev/ttyUSB1',
            '/dev/ttyUSB2',
            '/dev/ttyUSB3',
            '/dev/ttyUSB4',
            '/dev/ttyUSB4',
            '/dev/ttyUSB5',
            '/dev/ttyS0',
            '/dev/ttyS1',
            '/dev/ttyS2',
            '/dev/ttyS3',
            '/dev/ttyS4',
            '/dev/ttyS5',
            '/dev/ttyAMA0',
            '/dev/ttyAMA1',
            '/dev/ttyACM0',
            '/dev/ttyACM1',
            '/dev/rfcomm0',
            '/dev/ircomm0',
            '/dev/cuau0'
        ],
        'midi': [
            '/dev/midi1',
            '/dev/snd/midiC1D0'
        ]



    }

    def __init__(self,
                 LucidID='00', siface="/dev/ttyUSB0", tout=1):
        """Define required data structures and serial interface

           siface  - serial interface, defaults to /dev/ttyUSB0
           LucidID - The ID target of the Unit, defaults to 00
           tout    - serial timeout, in seconds, defaults to 1
        """
        self.ANALOG_GAIN = []

        # our 'config'
        self.glucidconf = configparser.ConfigParser()
        self.glucidconf.read(os.path.join(os.path.expanduser('~'), CONFIGFILE))
        # our serial connection
        # and default timeout
        self.conn = False
        self.tout = tout

        # our serial interface
        self.siface = siface

        # our baud rate
        self.baud=9600

        # InstanceID or LucidID 0-7
        self.INSTANCEID = LucidID

        # we either haven't connected
        # or had a failure
        self.error_flag = True

        self.curr_dig1val = 1
        
        # we had a device mismatch
        self.device_mismatch = False

        # our local representation of analog channel gain
        # 16 ... 8 ins then 8 outs
        # we store these values internally as integers in the
        # range that the lucid understands
        # we return strings representing db (-96)
        # we convert to hex when writing to Lucid
        self.gainlist = []

    def write_configfile(self):
        """Write the glucidconf to config file"""
        newconfig = open(os.path.join(os.path.expanduser('~'), CONFIGFILE), 'w')
        logging.info("Writing config to  %s" % os.path.join(os.path.expanduser('~'), CONFIGFILE))
        self.glucidconf.write(newconfig)
        newconfig.close()


        
    def set_device_from_configfile(self):
        # load config from file
        if 'Device' in self.glucidconf['DEFAULT']:
            self.siface = self.glucidconf['DEFAULT']['Device']
            logging.info("Read default %s from configfile" % self.siface)

    def is_in_linked(self):
        if 'LINKINCH' in self.glucidconf['DEFAULT']:
            retval = int(self.glucidconf['DEFAULT']['LINKINCH'])
        else:
            retval = 0
        return retval

    def is_out_linked(self):
        if 'LINKOUTCH' in self.glucidconf['DEFAULT']:
            retval = int(self.glucidconf['DEFAULT']['LINKOUTCH'])
        else:
            retval = 0
        return retval

    def get_aes_source(self, RETSTRING=True):
        """Send the GetAesSrc command and
        Get the currently set source of AES
        Digital Output.  Return
        String representation of result.

        If RETSTRING is FALSE return the raw value
        """
        DEFAULT_AES_SRC = 0 # Analog In
        retval = self.sendCommand('GetAesSrc')

        if not retval:
            raise ValueError("Bad Data Received")
            retval = 0
        else:
            retval = retval[0]

        if RETSTRING:
            return self.AES_SRC[retval]
        else:
            return retval

    def set_aes_src(self, srcval=False):
        """Set the source of the AES Digital
        OUTPUT.

        srcval - 0 : ADAT IN
                 1 : Analog IN
        """

        if int(srcval) < 0 or int(srcval) > 1:
            logging.error("set_aes_source value %s invalid!" % srcval)
            return False
        logging.info("set_aes_src:setting to %s" % self.AES_SRC[srcval])
        self.glucidconf['DEFAULT']['AES_SRC'] = str(srcval)
        self.sendCommand('SetAesSrc', [self.int_to_hex(srcval)])

        
    def get_instanceid(self):
        """return the currently set instanceid without
           retrieving it first, instanceid defaults to 00
           but is updated each time the Unit is read from"""
        return self.INSTANCEID

    def get_opt_source(self, RETSTRING=True):
        """Get the source of the ADAT Digit
        Input by sending the GetOptSrc command
        """
        DEFAULT_OPTICAL_SRC = 0 # Analog In

        retval = self.sendCommand('GetOptSrc')
        retval = retval[0]
            
        if RETSTRING:
            return self.OPTICAL_SRC[retval]
        else:
            return retval

    def set_opt_src(self, srcval=False):
        """Set the source of the ADAT Digital
        OUTPUT.

        srcval - 0 : Analog IN
                 1 : AES IN
        """

        if int(srcval) < 0 or int(srcval) > 1:
            logging.error("set_source value %s invalid!" % srcval)
            return False
        logging.info("set_opt_src: setting to %s" %
                     self.OPTICAL_SRC[srcval])
        self.glucidconf['DEFAULT']['OPTICAL_SRC'] = str(srcval)
        self.sendCommand('SetOptSrc', [self.int_to_hex(srcval)])

    def get_analog_source(self, RETSTRING=True):
        DEFAULT_ANALOG_SRC = 0 # ADAT In

        retval = self.sendCommand('GetAnalogSrc')
        retval = retval[0]
            
        if RETSTRING:
            return self.ANALOG_SRC[retval]
        else:
            return retval

    def set_analog_src(self, srcval=False):
        """Set the source of the Analog OUTPUT.

        srcval - 0 : ADAT IN
                 1 : AES IN
        """

        if int(srcval) < 0 or int(srcval) > 1:
            logging.error("set_source value %s invalid!" % srcval)
            return False
        logging.info("set_analog_src: setting to %s" %
                     self.ANALOG_SRC[srcval])
        self.glucidconf['DEFAULT']['ANALOG_SRC'] = str(srcval)
        self.sendCommand('SetAnalogSrc', [self.int_to_hex(srcval)])

    def get_sync_source(self, RETSTRING=True):
        """Get the source for clock sync and return
        a String representation

        If RETSTRING is FALSE, return the raw value
        """
        DEFAULT_SYNC = 1 # Wordclock
        
        retval = self.sendCommand('GetSync')
        if isinstance(retval, list):
            retval = retval[0]
        else:
            raise ValueError("Bad Data Recieved")
        retval = 0

            
        if RETSTRING:
            return self.SYNC[retval]
        else:
            return retval

    def set_sync_source(self, syncsrc=False, RETSTRING=True):
        """Set the source for clock sync

        syncsrc - 0 : ADAT
                  1 : WordClock
                  2 : INTERNAL 44.1
                  3 : INTERNAL 48
                  4 : AES 1
                  5 : AES 2
                  6 : AES 3
                  7 : S/PDIF
        """
        if (syncsrc < 0 or syncsrc > 7) and syncsrc not in self.SYNC:
            logging.error("set_sync_source value %s invalid!" % syncsrc)
            return False
        synchex = '{:02}'.format(syncsrc, 'x')
        logging.info("set_sync_source: set to %s" % self.SYNC[syncsrc])
        logging.info("set_sync_source: set to %s" % synchex)
        self.glucidconf['DEFAULT']['SYNC'] = str(synchex)
        self.sendCommand('SetSync', [synchex])


    def get_meter(self, RETSTRING=True):
        """Get the source for the front meters of the 8824
        """
        DEFAULT_METER = 2 # Analog Out
        
        retval = self.sendCommand('GetMode')
        retval = int("{0:02b}".format(retval[0])[-2:], 2)
            
        if RETSTRING:
            return self.METER[retval]
        else:
            return retval

    def set_meter_and_dig1(self, metersrc=False):
        """Set the source for front meters of the 8824
        AND to route S/SPIF

        metersrc - 0 : Meter Analog IN
                       AES DIG IN 1,2
                   1 : Digital IN
                       AES DIG IN 1,2
                   2 : Analog OUT
                       AES DIG IN 1,2
                   3 : Digital OUT
                       AES DIG IN 1,2
                   4 : Analog IN
                       S/PDIF DIG IN 1,2
                   5 : Digital IN
                       S/PDIF DIG IN 1,2
                   6 : Analog OUT
                       S/PDIF DIG IN 1,2
                   7 : Digital OUT
        """

        if int(metersrc) < 0 or int(metersrc) > 7:
            logging.error("set_meter_source val %s invalid!" % metersrc)
            return False

        modeval = int(metersrc)
        modeval = self.int_to_hex(modeval)
        logging.info("set_meter_and_dig1: setting MODE to %s" % modeval)
        if int(modeval) < 4:
            self.glucidconf['DEFAULT']['DIG1'] = '0'
            tmpval = modeval
        else:
            tmpval = int(modeval)-4
            self.glucidconf['DEFAULT']['DIG1'] = '1'
        self.glucidconf['DEFAULT']['METER']=str(tmpval)
        self.sendCommand('SetMode', [modeval])

    def set_meter(self, metersrc=False):
        """Set the source for front meters of the 8824

        metersrc - 0 : Analog IN
                   1 : Digital IN
                   2 : Analog OUT
                   3 : Digital OUT
        """

        if int(metersrc) < 0 or int(metersrc) > 3:
            logging.error("set_meter_source val %s invalid!" % metersrc)
            return False
        logging.info("set_meter: setting to %s" % self.METER[metersrc])

        curr_dig1 = self.get_dig1(False)
            
        logging.info("set_meter: Dig1 is %s" % curr_dig1)

        modeval = (int(curr_dig1)*4)+int(metersrc)
        modeval = self.int_to_hex(modeval)
        logging.info("set_meter: setting MODE to %s" % modeval)
        self.glucidconf['DEFAULT']['METER']=str(metersrc)
        self.sendCommand('SetMode', [modeval])

    def get_dig1(self, RETSTRING=True):
        """Get the source of Digital Channels 1,2
        Input (AES of SPDIF) by sending the GetMode command
        """
        DEFAULT_DIG1 = 1 # SPDIF
        
        retval = self.sendCommand('GetMode')
        retval = int("{0:04b}".format(retval[0])[-3], 2)            

        if RETSTRING:
            return self.DIG1[retval]
        else:
            return retval
        
    def set_dig1(self, srcval=False):
        """Set the source for Digital Channels 1,2:

        srcval - 0 : AES
                 1 : S/PDIF
        """

        if int(srcval) < 0 or int(srcval) > 1:
            logging.error("set_dig1 value %s invalid!" % srcval)
            return False
        logging.info("set_dig1: setting to %s" % self.DIG1[srcval])
        curr_meter = self.get_meter(False)
        logging.info("set_dig1: meter is %s" % curr_meter)

        modeval = (int(srcval)*4)+int(curr_meter)
        modeval = self.int_to_hex(modeval)
        logging.info("set_meter: setting MODE to %s" % modeval)
        self.glucidconf['DEFAULT']['DIG1']=str(srcval)
        self.sendCommand('SetMode', [modeval])

    @staticmethod
    def gain_int_to_db_string(intval):
        """Substract 96 and return the signed value as a string
        """
        if (intval-96) >= 0:
            return "+"+str(intval-96)
        return str(intval-96)

    @staticmethod
    def int_to_hex(intval):
        """A convenience function, use format to convert int to hex"""
        if type(intval) == "string":
            intval = int(intval)
        return '{:02}'.format(intval, 'x')

    @staticmethod
    def get_device_from_cfg():
        """Read the default device stored in our config file"""
        tmpconfig = configparser.ConfigParser()
        tmpconfig.read(os.path.join(os.path.expanduser('~'), CONFIGFILE))
        if 'Device' in tmpconfig['DEFAULT']:
            return tmpconfig['DEFAULT']['Device']
        else:
            return '/dev/ttyUSB0'


    def get_gain(self):
        """Populates the internal datastructure `gainlist` by
        sending the `GetAnalogGain` command to the 8824
        """
        # this returns a list of strings
        # representing dB
        # it also updates the gainlist

        # lucidgainlist... get from Lucid
        DEFAULT_GAINLIST = '88,88,88,88,88,88,88,88,97,97,97,97,97,97,97,97'

        retlist = []
        self.gainlist = []
        
        lgainlist = self.sendCommand('GetAnalogGain')
        self.gainlist = []
        self.log_gain_list(lgainlist)

        # the lucid reverses this 8..1 8..1
        # which we didn't know until too late
        # so we fix this here:
        self.gainlist = lgainlist[7::-1] + lgainlist[15:7:-1]
        
        for i in range(0, len(self.gainlist)):
            retlist.append(
                Glucid8824.gain_int_to_db_string(int(self.gainlist[i])))

        logging.info("Returning Gainlist")
        logging.info(retlist)
        return retlist

    def log_gain_list(self, gainlist=False):
        """Log the current gainlist, for testing purposes
        """
        if not gainlist:
            return False

        for g in self.gainlist:
            logging.info("%s" % Glucid8824.gain_int_to_db_string(int(g)))

    def update_channel_in_gainlist(self, gain=False, channel=False):
        """Update a single channel in the gain list, must have
        called get_gain to get the list from the 8824 first.

        gain    - value to set gain to -95 to +32
        channel - channel to set
        """
        logging.info("update_channel_in_gainlist: %s to %s" %
                     (channel, gain))

        channel = int(channel)
        # makes sure gain and channel is set
        if (channel < 0 or channel > 15):
            logging.error("update_channel_in_gainlist: bad channel value")
            return False

        # need to read all channels before writing one
        if (len(self.gainlist) < 15):
            logging.error("update_channel_in_gainlist: call get_gain first")
            return False

        # Replace the one channel gain
        logging.info("update_channel_in_gainlist: Current gainlist:")
        self.log_gain_list(self.gainlist)

        self.gainlist[channel] = int(gain)+96

        # set back the new gain
        logging.info("set_gain: New gainlist:")
        self.log_gain_list(self.gainlist)

    def set_gainlist_all_stage(self, gain=-99, input_or_output=0):
        """Set all input or output channels to the same gain value

        gain - integer -95 to 32

        input_or_output -  0: INPUT
                           1: OUTPUT
        """

        # input=0 ; output=1
        # gain is a string -95 +32
        if int(gain) < -95 or int(gain) > 32:
            logging.error("set_gainlist_all_stage: out of range %s" %
                          gain)
            return False

        gain = int(gain)
        logging.info("set_gainlist_all_stage: % , %s" % (gain, channel))

        if (input_or_output != 0 and input_or_output != 1):
            logging.error("set_gainlist_all_stage:channel not 0 or 1 :%s" %
                          channel)
            return False

        if (len(self.gainlist) < 15):
            logging.error("set_gainlist_all_stage: call get_gain first")
            return False

        # Replace half the gain
        logging.info("set_gainlist_all_stage: Current gainlist:")
        log_gain_list(self.gainlist)

        chstart = 8 * input_or_output
        for channel in range(chstart, chstart + 8):
            self.gainlist[channel] = int(gain) + 96
            logging.info("set_gainlist_all_stage: set %s to %d" %
                         (channel, int(gain)+96))

        # set back the new gain
        logging.info("set_gainlist_all_stage: New gainlist:")
        for g in self.gainlist:
            logging.info("%s" % Glucid8824.gain_int_to_db_string(g))

    def write_gainlist_to_lucid(self):
        """Convert `gainlist` to hex and call `SetAnalogGain`
        to write the values to the 8824
        """
        # we have to convert our local gainlist to hex
        # and use sendCommand to write it.
        # first we need to put the channels
        # in the ordering the lucid likes:
        # 8..1 8..1
        lucidgainlist = [];
        lucidgainlist = self.gainlist[7::-1] + self.gainlist[15:7:-1]

        cmdArg = []
        for chgain in lucidgainlist:
            chgain = hex(int(chgain))[2:]
            cmdArg.append(chgain)
            logging.info("write_gainlist_to_lucid: add %s to cmdArg" %
                         (chgain))

        logging.info("write_gainlist_to_lucid: calling sendCommand")
        
        self.sendCommand('SetAnalogGain', cmdArg)

    ###########################
    # Begin lower-level methods
    ###########################

    def sendCommand(self, cmdkey, cmdArg=['00'], checkcommand=True):
        # if checkcommand is False we can use values outside
        # of our command dictionary.  Good for looking for undocumented
        # commands
        if checkcommand and cmdkey not in self.COMMANDSET:
            logging.error("SendCommand: Invalid Command Key: %s", cmdkey)
            return False

        logging.info('sendCommand sending %s:%s',
                     cmdkey,
                     self.COMMANDSET[cmdkey])
        if self.error_flag:
            logging.error("SendCommand: Error Flag - aborting command")
            return False

        cmd = ""
        cmd += self.STARTBYTE+' '
        for hexcode in self.LUCIDINCID:
            cmd += hexcode+' '
        cmd += self.MODELID+' '
        cmd += '{:02}'.format(int(self.INSTANCEID))+' '
        cmd += self.COMMANDSET[cmdkey]+' '
        for cmdargs in cmdArg:
            cmd += cmdargs+' '
        cmd += self.ENDBYTE
        logging.info('sendCommand: Sending \"%s\"', cmd)

        self.conn.write(bytes.fromhex(cmd))

        if self.siface in self.DEVICES['rs232'] :
            logging.info("siface is %s"%self.siface)
            hexdata = self.getLinefromSerial()
            if not hexdata:
                logging.error("Did NOT receive data response.")
                return False
            return self.getResponse(cmdkey, hexdata)
        return True
    
    def getResponse(self, cmdkey, hexdata):
        """Parse the hex data received, set error flags
        if the repsponse is poorly formed
        """

        logging.info("getResponse: Length of hexdata is %s", len(hexdata))
        # if logging print out our response
        for i in range(0, len(hexdata)):
            logging.info("hexdata[%s]:%s", i, format(hexdata[i], '#04x'))

        retdata = []
        if self.error_flag:
            print("Error Flag is set, not attempting response")
            return False

        if not self.isValidHexData(hexdata):
            logging.error("getReponse received Error from isValidHexData")
            return False

        # get the beginning of the command
        StartIndex = hexdata.index(int(self.STARTBYTE, 16))

        # we are getting a response
        if hexdata[StartIndex+6] != int('0x05', 16):
            logging.error("getLucidResponse looking for OxO5:%s",
                          hexdata[StartIndex+6])
            return False

        # expect response to be same as command issued
        # clean this up?  all cases been checked?
            logging.error("failed at verifying commandkey %s:%s ",
                          self.COMMANDSET[cmdkey], hexdata[StartIndex+7])
            return False

        retindex = StartIndex + 8
        while ((retindex < len(hexdata))
                and (hexdata[retindex] != int(self.ENDBYTE, 16))):
            logging.info("appending %s to response string",
                         hexdata[retindex])
            retdata.append(hexdata[retindex])
            retindex += 1
        return retdata

    def isValidHexData(self, hexdata):
        """Check for a well formed instruction"""
        # Have a Valid Start Byte?
        try:
            StartIndex = hexdata.index(int(self.STARTBYTE, 16))
        except ValueError:
            logging.error("isValidHexData failed to find StartIndex")
            return False
        # Have a Valid End Byte?
        try:
            hexdata.index(int(self.ENDBYTE, 16))
        except ValueError:
            logging.error("isValidHexData failed at finding ENDBYTE")
            return False

        # Have a Valid Manufacturer Id?
        for i in range(3):
            if hexdata[StartIndex+1+i] != int(self.LUCIDINCID[i], 16):
                logging.error("isValidHexData:%s failed manufacturer id",
                              StartIndex+1+i)
                return False

        # Have a Valid ModelId?
        if hexdata[StartIndex+4] != int(self.MODELID, 16):
            logging.error("isValidHexData:%s failed at modelId",
                          StartIndex+1+i)
            return False

        # Read and Update InstanceID should be last.
        # If we are receiving the wrong InstanceID
        # set the INSTANCEIDDIRTY flag
        if hexdata[StartIndex+5] != int(self.INSTANCEID, 16):
            logging.warning("isValidHexData: unexpected InstanceId - %s",
                            hexdata[StartIndex+5])
            logging.warning("isValidHexData Updating from %s to %s",
                            self.InstanceId, hexdata[StartIndex+5])
            self.INSTANCEID = hexdata[StartIndex+5]
            self.device_mismatch = True
            return False
        else:
            # clear device mismatch flag if set
            self.device_mismatch = False
        return True

    def connect(self):
        """Attempt to open a serial connection to self.siface
        """
        logging.info("LucidConnection running connect")

        try:
            logging.info("LucidConnection opening rs232 device %s"%self.siface)
            self.conn = serial.Serial(self.siface, baudrate=self.baud, timeout=self.tout)
        except serial.SerialException as se:
            logging.error("Could not open connection %s", self.siface)
            self.error_flag = True
            return False
        except Exception as e:
            logging.error("Could not open connection %s", self.siface)
            self.error_flag = True
            return False
        else:
            self.error_flag = False

            return True
        

    def disconnect(self):
        """Close serial connection"""
        try:
            self.conn.close()
        except serial.SerialException as se:
            self.error_flag = True
            logging.error("Could not close serial connection %s", self.siface)

    def get_iface(self):
        """Return the currently set serial interface"""
        return self.siface

    def clear_errorflag(self):
        """set error_flag and device_mismatch to False"""
        self.error_flag = False
        self.device_mismatch = False

    def set_errorflag(self):
        self.error_flag = True

    def getLinefromSerial(self):
        """Returns a line of data from the serial connection"""
        if self.error_flag:
            logging.warning("getLinefromSerial not connected")
            self.set_errorflag()
            return False

        # we try 10 times
        for i in range(0, 3):
            myline = self.conn.readline()
            logging.info("Received %s bytes", len(myline))
            if len(myline) > 0:
                break
            if i == 9:
                return False
        return myline
