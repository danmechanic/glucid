#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
glucid8824.py defines a class `Glucid8824` which
implements an api to a Lucid 8824 Analog/Digital Audio Converter
RS232 interface over a serial port.

A `main` and associated functions provide a useful
command line tool `glucid` to configure the Lucid 8824/.

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

__version__ = '0.1.3a'
__author__ = 'Daniel R Mechanic (dan.mechanic@gmail.com)'

import logging
import getopt
import sys
import serial
from distutils.util import strtobool
from _ast import Or


class Glucid8824:
    """The Glucid8824 class represents a single Lucid
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

    def __init__(self,
                 LucidID='00', siface="/dev/ttyUSB0", tout=1):
        """Define required data structures and serial interface

           siface  - serial interface, defaults to /dev/ttyUSB0
           LucidID - The ID target of the Unit, defaults to 00
           tout    - serial timeout, in seconds, defaults to 1
        """
        self.ANALOG_GAIN = []

        # our serial connection
        # and default timeout
        self.conn = False
        self.tout = tout

        # our serial interface
        self.siface = siface

        # InstanceID or LucidID 0-7
        self.INSTANCEID = LucidID

        # we either haven't connected
        # or had a failure
        self.error_flag = True

        # we had a device mismatch
        self.device_mismatch = False

        # our local representation of analog channel gain
        # 16 ... 8 ins then 8 outs
        # we store these values internally as integers in the
        # range that the lucid understands
        # we return strings representing db (-96)
        # we convert to hex when writing to Lucid
        self.gainlist = []

    def get_aes_source(self, RETSTRING=True):
        """Send the GetAesSrc command and
        Get the currently set source of AES
        Digital Output.  Return
        String representation of result.

        If RETSTRING is FALSE return the raw value
        """
        retval = self.sendCommand('GetAesSrc')

        if RETSTRING and retval:
            return self.AES_SRC[retval[0]]
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

        retval = self.sendCommand('GetOptSrc')
        if RETSTRING and retval:
            return self.OPTICAL_SRC[retval[0]]
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
        self.sendCommand('SetOptSrc', [self.int_to_hex(srcval)])

    def get_analog_source(self, RETSTRING=True):
        retval = self.sendCommand('GetAnalogSrc')
        if RETSTRING and retval:
            return self.ANALOG_SRC[retval[0]]
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
        self.sendCommand('SetAnalogSrc', [self.int_to_hex(srcval)])

    def get_sync_source(self, RETSTRING=True):
        """Get the source for clock sync and return
        a String representation

        If RETSTRING is FALSE, return the raw value
        """
        retval = self.sendCommand('GetSync')
        if RETSTRING and retval:
            return self.SYNC[retval[0]]
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
        self.sendCommand('SetSync', [synchex])

    def get_meter(self, RETSTRING=True):
        """Get the source for the front meters of the 8824
        """
        retval = self.sendCommand('GetMode')
        meterval = False

        if retval:
            meterval = int("{0:02b}".format(retval[0])[-2:], 2)
        else:
            return False

        if RETSTRING and retval:
            return self.METER[meterval]
        elif retval:
            return meterval
        else:
            retval

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

        self.sendCommand('SetMode', [modeval])

    def get_dig1(self, RETSTRING=True):
        """Get the source of Digital Channels 1,2
        Input (AES of SPDIF) by sending the GetMode command
        """
        retval = self.sendCommand('GetMode')

        if retval:
            dig1val = int("{0:04b}".format(retval[0])[-3], 2)
        else:
            return False

        if RETSTRING:
            return self.DIG1[dig1val]
        else:
            return dig1val

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

    def get_gain(self):
        """Populates the internal datastructure `gainlist` by
        sending the `GetAnalogGain` command to the 8824
        """
        # this returns a list of strings
        # representing dB
        # it also updates the gainlist

        # lucidgainlist... get from Lucid
        lgainlist = self.sendCommand('GetAnalogGain')
        retlist = []

        self.gainlist = []

        self.log_gain_list(lgainlist)
        for i in range(0, len(lgainlist)):
            # update our gainlist
            self.gainlist.append(lgainlist[i])
            retlist.append(
                Glucid8824.gain_int_to_db_string(lgainlist[i]))
        return retlist

    def log_gain_list(self, gainlist=False):
        """Log the current gainlist, for testing purposes
        """
        if not gainlist:
            return False

        for g in gainlist:
            logging.info("%s" % Glucid8824.gain_int_to_db_string(g))

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
        cmdArg = []
        for chgain in self.gainlist:
            chgain = hex(chgain)[2:]
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
        cmd += self.INSTANCEID+' '
        cmd += self.COMMANDSET[cmdkey]+' '
        for cmdargs in cmdArg:
            cmd += cmdargs+' '
        cmd += self.ENDBYTE
        logging.info('sendCommand: Sending \"%s\"', cmd)
        self.conn.write(bytes.fromhex(cmd))
        hexdata = self.getLinefromSerial()
        if not hexdata:
            logging.error("Did NOT receive data response.")
            return False
        return self.getResponse(cmdkey, hexdata)

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
            self.conn = serial.Serial(self.siface, timeout=self.tout)
        except serial.SerialException as se:
            logging.error("Could not open serial connection %s", self.siface)
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


def banner():
    progname = str(sys.argv[0].split('/')[-1])
    print('-'*40)
    # print("glucid: The Lucid 8824 Tool")
    # print("%s version %s" %
    #      (progname, str(__version__))
    #      )
    print("\nglucid and glucid8824.py:")
    print("Copyright (C) 2017,2018 Daniel R Mechanic")
    print("GPL version 3 ONLY <http://gnu.org/licenses/gpl.html>.")
    print("This program comes with ABSOLUTELY NO WARRANTY;")
    print("This is free software, and you are welcome to")
    print("change and redistribute it under certain circumstances;")
    print("For details see LICENSE")
    print('-'*40)


def usage_light():
    print("Usage: "+sys.argv[0].split('/')[-1]+" [OPTION]... ")
    print("Try '"+sys.argv[0].split('/')[-1]+" --help' for more information")


def usage():
    print("")
    print("Usage: "+sys.argv[0].split('/')[-1]+" [OPTION]... ")
    print("Get or Set Values on a Lucid8824 Interface")
    print("")
    print("OPTIONS:")
    print("  -h,--help\tthis help")
    print("  -v,--verbose\tverbose output")
    print("  -d DEVICE\tUse DEVICE instead of /dev/ttyUSB0")
    print("\nGET OPTIONS:")
    print("  -g,--get_all\tget all values from lucid")
    print("  --get_sync\tget source of clock sync")
    print("  --get_analog\tget source of analog output")
    print("  --get_aes\tget source of aes output")
    print("  --get_opt\tget source of optical output")
    print("  --get_meter\tget source of meters")
    print("  --get_dig1\tget output of digital channels 1&2")
    print("  --get_gain\tget analog gain settings")
    print("\nSET OPTIONS:")
    print("  --set_sync=SYNC\tset source to sync to SYNC")
    print("        \tSYNC is a number 0-7:")
    print("         \t0 -'ADAT'")
    print("         \t1 -'WordClock'")
    print("         \t2 -'44.1 internal'")
    print("         \t3 -'48 Internal'")
    print("         \t4 -'AES In1'")
    print("         \t5 -'AES In2'")
    print("         \t6 -'AES In3'")
    print("         \t7 -'S/PDIF In'")
    print("")
    print("  --set_analog=SRC\tset analog output source to SRC")
    print("        \tSRC is a number 0 or 1:")
    print("         \t0 -'ADAT In'")
    print("         \t1 -'AES In'")
    print("")
    # TODO: This is commented out because it does not appear to work :-/
    # print("  --set_aes=SRC\tset aes output source to SRC")
    # print("        \tSRC is a number 0 or 1:")
    # print("         \t0 -'ADAT In'")
    # print("         \t1 -'Analog In'")
    # print("")
    print("  --set_opt=SRC\tset optical output source to SRC")
    print("        \tSRC is a number 0 or 1:")
    print("         \t0 -'Analog In'")
    print("         \t1 -'AES In'")
    print("")
    print("  --set_meter=METER\tset meters to METER")
    print("        \tMETER is a number 0-3:")
    print("         \t0 -'Analog In'")
    print("         \t1 -'Digital In'")
    print("         \t2 -'Analog Out'")
    print("         \t3 -'Digital Out'")
    print("")
    print("  --set_dig1=DIGIN\tset digital inputs 1,2 to DIGIN")
    print("        \tDIGIN is 0 or 1:")
    print("         \t0 -'AES 1,2'")
    print("         \t1 -'S/PDIF'")
    print("")
    print("  --sci,--set_channel_input_gain=GAIN CHANNEL [CHANNEL...] \n\t \
        set analog INPUT gain of CHANNELs to GAIN")
    print("        \tGAIN is an integer value between -95 and +32")
    print("        \tCHANNELs are integer values between 1-8:")
    print("         \t\t1-8 -'INPUT Channels 1-8'")
    print("")
    print("  --sco,--set_channel_output_gain=GAIN CHANNEL [CHANNEL...] \n\t \
        set analog OUTPUT gain of CHANNELs to GAIN")
    print("        \tGAIN - an integer value between -95 and +32")
    print("        \tCHANNELs - integer values between 1-8:")
    print("         \t\t1-8 -'OUTPUT Channels 1-8'")
    print("")
    print("  --set_gain=PRESET")
    print("\t set analog INPUTS and OUTPUT to recommended PRESET")
    print("        \tPRESET is an integer value +4 or -10:")
    print("         \t'+4' -Sets all INPUTS to -8dB and all OUTPUTS to +1dB")
    print("         \t'-10' -Sets all INPUTS to +4dB and all OUTPUTS to -11dB")


def get_aes_src(lucid):
    """Call lucid8824.get_aes_source, exit on failure"""
    print("AES Source:\t%s" % (lucid.get_aes_source() or
                               sys.exit("failed talking to Lucid")))


def get_analog_src(lucid):
    """Call lucid8824.get_analog_source, exit on failure"""
    print("Analog Source:\t%s" % (lucid.get_analog_source() or
                                  sys.exit("failed talking to 8824")))


def get_opt_src(lucid):
    """Call lucid8824.get_opt_source, exit on failure"""
    print("Optical Source:\t%s" % (lucid.get_opt_source() or
                                   sys.exit("failed talking to 8824")))


def get_meter(lucid):
    """Call lucid8824.get_meter, exit on failure"""
    print("Meter:\t\t%s" % (lucid.get_meter() or
                            sys.exit("failed talking to 8824")))


def get_sync(lucid):
    """Call lucid8824.get_sync, exit on failure"""
    print("Sync:\t\t%s" % (lucid.get_sync_source() or
                           sys.exit("failed talking to 8824")))


def get_dig1(lucid):
    """Call lucid8824.get_dig1, exit on failure"""
    print("Dig Input 1,2:\t%s" % (lucid.get_dig1() or
                                  sys.exit("failed talking to 8824")))


def get_gain(lucid):
    """Call lucid8824.get_get, exit on failure"""
    gainlist = lucid.get_gain() or sys.exit("failed talking to Lucid")
    print("Analog Gain:")
    print(' '*40)
    print('***************************************')
    print('Recommended: +4dBu: IN -8 dB OUT  +1 dB')
    print('            -10dBV: IN +4 dB OUT -11 dB')
    print('***************************************')
    print(' '*40)
    for i in range(1, 9):
        print('\tChannel {0:1d}: IN {1:3s}dB OUT  {2:3s}dB'
              .format(i, gainlist[i-1], gainlist[i+7]))


def set_gain_channels(lucid, gain=-99, channel_list=[]):
    """Set the channels in `channel_list` to `gain`
    Write these values to the 8824
    """
    gain = int(gain)
    logging.info("set_gain_channels: value of gain is %s" % gain)
    if (type(channel_list) != list):
            logging.critical("list received: %s" %
                             type(channel_list))
            sys.exit(1)
    elif (gain < -95 or
            gain > 32):
            logging.critical("bad argument to set_gain_channels: %s" %
                             gain)
            sys.exit(1)
    for i in channel_list:
        if int(i) < 0 or int(i) > 15:
            logging.critical("channel index out of range")
            sys.exit(1)

    logging.info("set_gain_channels: calling get_gain...")
    lucid.get_gain() or sys.exit("failed talking to 8824")

    logging.info("set_gain_channels: updating gainlist")
    for ch in channel_list:
        logging.info("set_gain_channels: setting channel %s to %s" %
                     (ch, gain))
        lucid.update_channel_in_gainlist(gain, ch)

    logging.info("set_gain_channels: writing gainlist to Lucid")
    lucid.write_gainlist_to_lucid()


def get_all(lucid):
    """Get all possible values from the 8824 by calling each
    function sequentially
    """
    get_sync(lucid)
    get_meter(lucid)
    get_analog_src(lucid)
    get_aes_src(lucid)
    get_opt_src(lucid)
    get_dig1(lucid)
    get_gain(lucid)


def set_sync(lucid, syncval):
    """Call lucid8824.set_sync_source"""
    lucid.set_sync_source(syncval)


def set_meter(lucid, meterval):
    """Call lucid8824.set_meter"""
    lucid.set_meter(meterval)


def set_dig1(lucid, srcval):
    """Call lucid8824.set_dig1"""
    lucid.set_dig1(srcval)


def set_analog_src(lucid, srcval):
    """Call lucid8824.set_analog_src"""
    lucid.set_analog_src(srcval)


def set_opt_src(lucid, srcval):
    """Call lucid8824.set_opt_src"""
    lucid.set_opt_src(srcval)


def set_aes_src(lucid, srcval):
    """Call lucid8824.set_aes_src"""
    lucid.set_aes_src(srcval)


def main():
    """Run the glucid8824 Command Line Interface"""

    lucid = False

    banner()

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hvgd:",
                                   [
                                       "help",
                                       "verbose",
                                       "get_all",
                                       "get_aes",
                                       "set_aes=",
                                       "get_analog",
                                       "set_analog=",
                                       "get_opt",
                                       "set_opt=",
                                       "get_sync",
                                       "set_sync=",
                                       "get_meter",
                                       "set_meter=",
                                       "get_gain",
                                       "set_gain=",
                                       "set_channel_input_gain=",
                                       "sci=",
                                       "set_channel_output_gain=",
                                       "sco=",
                                       "get_dig1",
                                       "set_dig1="
                                ]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    verbose = False
    # if not default serial interface
    serialif = False
    # first parse for verbose option
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
            logging.basicConfig(level=logging.INFO)

    if verbose:
        logging.basicConfig(level=logging.INFO)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-d"):
            serialif = a
            logging.info("setting serialif to %s" % serialif)

    if serialif:
        logging.info("serialif is %s" % serialif)
        lucid = Glucid8824(siface=serialif)
    else:
        lucid = Glucid8824()

    if not lucid.connect():
        sys.exit("Failed to open connection using %s \n" %
                 lucid.get_iface())

    print("Using %s to connect to lucid ID %s\n" %
          (lucid.get_iface(), lucid.get_instanceid()))

    for o, a in opts:
        if o in ("-h", "--help", "-v", "--verbose", "-d"):
            continue
        elif o in ("-g", "--get_all"):
            logging.info("get all")
            get_all(lucid)
            sys.exit(0)
        elif o in ("--get_aes"):
            logging.info("get aes src")
            get_aes_src(lucid)
        elif o in ("--set_aes"):
            if int(a) >= 0 and int(a) <= 1:
                logging.info("setting aes to %s" % a)
                set_aes_src(lucid, int(a))
                get_aes_src(lucid)
            else:
                logging.critical("bad argument to set_aes_src")
                usage()
                sys.exit(1)
        elif o in ("--get_analog"):
            logging.info("get analog src")
            get_analog_src(lucid)
        elif o in ("--set_analog"):
            if int(a) >= 0 and int(a) <= 1:
                logging.info("setting analog to %s" % a)
                set_analog_src(lucid, int(a))
                get_analog_src(lucid)
            else:
                logging.critical("bad argument to set_analog_src")
                usage()
                sys.exit(1)
        elif o in ("--get_opt"):
            logging.info("get aes src")
            get_opt_src(lucid)
        elif o in ("--set_opt"):
            if int(a) >= 0 and int(a) <= 1:
                logging.info("setting optical to %s" % a)
                set_opt_src(lucid, int(a))
                get_opt_src(lucid)
            else:
                logging.critical("bad argument to set_opt_src")
                usage()
                sys.exit(1)
        elif o in ("--get_sync"):
            logging.info("get sync")
            get_sync(lucid)
        elif o in ("--set_sync"):
            if int(a) >= 0 and int(a) <= 7:
                logging.info("setting sync to %s" % a)
                set_sync(lucid, int(a))
                get_sync(lucid)
            else:
                logging.critical("bad argument to set_sync")
                usage()
                sys.exit(1)
        elif o in ("--get_meter"):
            logging.info("get meter")
            get_meter(lucid)
        elif o in ("--set_meter"):
            if int(a) >= 0 and int(a) <= 3:
                logging.info("setting meter to %s" % a)
                set_meter(lucid, int(a))
                get_meter(lucid)
            else:
                logging.critical("bad argument to set_meter")
                usage()
                sys.exit(1)
        elif o in ("--get_dig1"):
            logging.info("get dig1")
            get_dig1(lucid)
        elif o in ("--set_dig1"):
            if int(a) >= 0 and int(a) <= 1:
                logging.info("setting dig1 to %s" % a)
                set_dig1(lucid, int(a))
                get_dig1(lucid)
            else:
                logging.critical("bad argument to set_dig1")
                usage()
                sys.exit(1)
        elif o in ("--get_gain"):
            logging.info("get gain")
            get_gain(lucid)
        elif o in ('--set_gain'):
            logging.info("set gain")
            if (int(a) != 4 and int(a) != -10):
                logging.critical("bad argument to set_gain")
                sys.exit(1)
            if int(a) == 4:
                set_gain_channels(lucid, -8, [0, 1, 2, 3, 4, 5, 6, 7])
                set_gain_channels(lucid, 1, [8, 9, 10, 11, 12, 13, 14, 15])
            elif int(a) == -10:
                set_gain_channels(lucid, 4, [0, 1, 2, 3, 4, 5, 6, 7])
                set_gain_channels(lucid, -11, [8, 9, 10, 11, 12, 13, 14, 15])
            get_gain(lucid)
        elif o in ('--sci', '--set_channel_input_gain',
                   '--sco', '--set_channel_output_gain'):
            # make sure gain value is valid
            if (
                int(a) < -95
                or int(a) > 32
                or len(args) == 0
               ):
                    logging.critical("Bad Argument: %s, %" % (o, a))
                    sys.exit(1)
            # make sure user chose channels to apply gain to
            elif(len(args) == 0):
                    logging.critical("No Channels Specified")
                    sys.exit(1)
            # make sure channels are valid
            for arg in args:
                if int(arg) < 1 or int(arg) > 8:
                    logging.critical("Invalid Channel: %s" % arg)
                    sys.exit(1)

            if o in ('--sci', '--set_channel_input_gain'):
                # Input Channels Index at Zero: 0-15
                set_gain_channels(lucid, int(a),
                                  [int(i) - 1 for i in args])
            elif o in ('--sco', '--set_channel_output_gain'):
                # Output Channels are 7-15
                set_gain_channels(lucid, int(a),
                                  [int(i) + 7 for i in args])

            get_gain(lucid)
        else:
            usage_light()
            sys.exit(0)


if __name__ == "__main__":
    main()
