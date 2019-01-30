#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
glucid8824.py defines a class `glucid8824` which
implements an api to a Lucid 8824 Analog/Digital Audio Converter
RS232 interface over a serial port.

A `main` and associated functions provide a useful
command line tool `glucid` in glucid.py to configure the Lucid 8824/.

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

__version__ = '0.4.0a'
__author__ = 'Daniel R Mechanic (dan.mechanic@gmail.com)'
CONFIGFILE='.glucid.cfg'

import configparser
import getopt
import logging
import os
import sys
from glucid8824 import Glucid8824

# BEGIN FUNCTIONS FOR COMMAND LINE INTERFACE

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
    print("Your Lucid MUST be in REMOTE MODE")
    print("DIP SWITCH 1 on your Lucid MUST be DOWN on POWER UP")
    print("All Switches should be left down for ID 00 in Remote Mode")
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
    print("  -D DEVICE\tUse DEVICE instead of /dev/ttyUSB0")
    print("         \tAND Set DEVICE as new default")
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
    print("  --set_meter_and_dig1=VALUE\tset meters and dig 1/2")
    print("        \tVALUE is a number 0-7:")
    print("         \t0 -'Meter Analog In, use aes for 1,2'")
    print("         \t1 -'Meter Digital In, use aes for 1,2'")
    print("         \t2 -'Analog Out, use aes for 1,2'")
    print("         \t3 -'Digital Out, use aes for 1,2'")
    print("         \t4 -'Meter Analog In, use s/pdif for 1,2'")
    print("         \t5 -'Meter Digital In, use s/pdif for 1,2'")
    print("         \t6 -'Analog Out, use aes s/pdif 1,2'")
    print("         \t7 -'Digital Out, use aes s/pdif 1,2'")
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
    print("\nGET OPTIONS:")
    print("**GET OPTIONS ARE FOR RS232 MODEL UNITS ONLY**")
    print("  -g,--get_all\tget all values from lucid")
    print("  --get_sync\tget source of clock sync")
    print("  --get_analog\tget source of analog output")
    print("  --get_aes\tget source of aes output")
    print("  --get_opt\tget source of optical output")
    print("  --get_meter\tget source of meters")
    print("  --get_dig1\tget output of digital channels 1&2")
    print("  --get_gain\tget analog gain settings")

def error_exit(errormsg="Fatal Error"):
    """Exit the command-line with 1 and a passed-in errormsg
    """
    logging.critical(errormsg)
    #usage()
    print("--help will provide usage options")
    sys.exit(1)

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
    print("Sync:\t\t%s" % (lucid.get_sync_source()))

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
    if lucid.siface in lucid.DEVICES['rs232']:
        get_sync(lucid)

def set_meter_and_dig1(lucid, meterval):
    """Call lucid8824.set_meter"""
    lucid.set_meter_and_dig1(meterval)
    if lucid.siface in lucid.DEVICES['rs232']:
        get_meter(lucid)
        get_dig1(lucid)

def set_meter(lucid, meterval):
    """Call lucid8824.set_meter"""
    if lucid.siface in lucid.DEVICES['rs232']:
        lucid.set_meter(meterval)
        get_meter(lucid)


def set_dig1(lucid, srcval):
    """Call lucid8824.set_dig1"""
    lucid.set_dig1(srcval)
    if lucid.siface in lucid.DEVICES['rs232']:
        get_dig1(lucid)


def set_analog_src(lucid, srcval):
    """Call lucid8824.set_analog_src"""
    lucid.set_analog_src(srcval)


def set_opt_src(lucid, srcval):
    """Call lucid8824.set_opt_src"""
    lucid.set_opt_src(srcval)
    if lucid.siface in lucid.DEVICES['rs232']:
        get_opt_src(lucid)
                
def set_aes_src(lucid, srcval):
    """Call lucid8824.set_aes_src"""
    lucid.set_aes_src(srcval)


def main():
    """Run the glucid8824 Command Line Interface"""

    lucid = False
    serialif = '/dev/ttyUSB0'
    device_id = '00'
    
    banner()

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hvmgd:D:i:",
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
                                       "set_dig1=",
                                       "set_meter_and_dig1=",
                                       "device_id="
                                ]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    verbose = False
    # if not default serial interface
    serialif = '/dev/ttyUSB0'
    # first parse for verbose option
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
            logging.basicConfig(level=logging.INFO)

    if verbose:
        logging.basicConfig(level=logging.INFO)

    # read interface from configfile
    glucidconf = configparser.ConfigParser()
    #glucidconf.read(CONFIGFILE)
    glucidconf.read(os.path.join(os.path.expanduser('~'), CONFIGFILE))

    if 'Device' in glucidconf['DEFAULT']:
        serialif = glucidconf['DEFAULT']['Device']
        logging.info("Read default %s from configfile" % serialif)
    if 'DEVICE_ID' in glucidconf['DEFAULT']:
        device_id = glucidconf['DEFAULT']['DEVICE_ID']
        logging.info("Read device_id %s from configfile" % device_id)

    newconfig = open(os.path.join(os.path.expanduser('~'), CONFIGFILE), 'w')
            
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-d"):
            # set device to user command line argument
            serialif = a
            logging.info("setting serialif to %s" % serialif)
        elif o in ("-D"):
            # set device to user command line argument
            # AND write to config file
            serialif = a
            logging.info("new default device %s" % serialif)
            glucidconf.set('DEFAULT','Device',serialif)
            newconfig.close()
        elif o in ("-i"):
            device_id = '{:02}'.format(int(a))
            logging.info("new default device_id %s" % device_id)
        elif o in ("-I"):
            device_id = '{:02}'.format(int(a))
            logging.info("new default device_id %s" % device_id)
            glucidconf.set('DEFAULT','DEVICE_ID',device_id)

    glucidconf.write(newconfig)
    logging.info("Wrote config to  %s" % os.path.join(os.path.expanduser('~'), CONFIGFILE))

    lucid = Glucid8824(siface=serialif,LucidID=device_id)

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
            else:
                logging.critical("bad argument to set_meter")
                usage()
                sys.exit(1)
        elif o in ("--set_meter_and_dig1"):
            if int(a) >= 0 and int(a) <= 7:
                logging.info("setting meter_dig1 to %s" % a)
                set_meter_and_dig1(lucid, int(a))
            else:
                logging.critical("bad argument to set_meter_and_dig1")
                usage()
                sys.exit(1)
        elif o in ("--get_dig1"):
            logging.info("get dig1")
            get_dig1(lucid)
        elif o in ("--set_dig1"):
            if int(a) >= 0 and int(a) <= 1:
                logging.info("setting dig1 to %s" % a)
                set_dig1(lucid, int(a))
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
