=============================
**glucid** Command Line Usage
=============================

Confirm you have a working installing of **glucid** by typing

``glucid``

.. note::

   To configure the Lucid 8824, you must have the unit in remote mode by setting DIP switch 1 to down.  See your owners manual for more information.

Know what Serial Port you are Using
===================================

By default, **glucid** assumes you are using **/dev/ttyUSB0**   Use the **-d** option if you are using a different Serial port.

.. note::

   OSX users may try **/dev/tty.usbserial** for a usb to serial convert; you may need to install an extra driver.  Windows users may try **COM1**
.. note::

   The user who is running glucid must be able to read
   and write to whichever serial device you are using; consult your
   operating system documentation.

Confirm Connection to Your Audio Converter
==========================================

First:

* Power Off your Lucid 8824
* Flip DIP Switch 1 on your Lucid 8824 to **down**  (remote)
* Connect a 9 pin Serial connector from the Lucid 8824 to your computer
* Power On your Lucid 8824
  
If all is well, you can confirm connection to your Audio Converter by
simply running **glucid**, for example: ::


  $ glucid
  ----------------------------------------

  glucid and glucid8824.py
  Copyright (C) 2017,2018 Daniel R Mechanic
  GPL version 3 ONLY <http://gnu.org/licenses/gpl.html>.
  This program comes with ABSOLUTELY NO WARRANTY;
  This is free software, and you are welcome to
  change and redistribute it under certain circumstances;
  For details see LICENSE
  ----------------------------------------
  Using /dev/ttyUSB0 to connect to lucid ID 00

A failed connection would give the error: ::

  Failed to open connection using /dev/ttyUSB0


Using a Serial device other than /dev/ttyUSB0 **-d**
----------------------------------------------------

To use a device other than /dev/ttyUSB0 use the **-d** switch to **glucid**: ::

  $ glucid -d /dev/ttyS0

  

Get All Current Values
======================

To get all current values, use **-g** or **--get_all**: ::

  
  $ glucid -g
  ----------------------------------------

  glucid and glucid8824.py
  Copyright (C) 2017,2018 Daniel R Mechanic
  GPL version 3 ONLY <http://gnu.org/licenses/gpl.html>.
  This program comes with ABSOLUTELY NO WARRANTY;
  This is free software, and you are welcome to
  change and redistribute it under certain circumstances;
  For details see LICENSE
  ----------------------------------------
  Using /dev/ttyUSB0 to connect to lucid ID 00

  Sync:		        WordClock
  Meter:		Analog In
  Analog Source:	ADAT In
  AES Source:	        ADAT In
  Optical Source:	Analog In
  Dig Input 1,2:	S/PDIF
  Analog Gain:
  
  ***************************************
  Recommended: +4dBu: IN -8 dB OUT  +1 dB
              -10dBV: IN +4 dB OUT -11 dB
  ***************************************
  
  Channel 1: IN -8 dB OUT  +1 dB
  Channel 2: IN -8 dB OUT  +1 dB
  Channel 3: IN -8 dB OUT  +1 dB
  Channel 4: IN -8 dB OUT  +1 dB
  Channel 5: IN -8 dB OUT  +1 dB
  Channel 6: IN -8 dB OUT  +1 dB
  Channel 7: IN -8 dB OUT  +1 dB
  Channel 8: IN -8 dB OUT  +1 dB

Get Individual Values
---------------------

The following options may be used to get other values: ::

  --get_sync	get source of clock sync
  --get_analog	get source of analog output
  --get_aes	get source of aes output
  --get_opt	get source of optical output
  --get_meter	get source of meters
  --get_dig1	get output of digital channels 1&2
  --get_gain	get analog gain settings



Setting Audio Levels
====================

Getting Current Audio Level Values
----------------------------------

Use the **--get_gain** option to glucid to get all Audio Levels: ::

  $ glucid --get_gain
  
  Channel 1: IN -8 dB OUT  +1 dB
  Channel 2: IN -8 dB OUT  +1 dB
  Channel 3: IN -8 dB OUT  +1 dB
  Channel 4: IN -8 dB OUT  +1 dB
  Channel 5: IN -8 dB OUT  +1 dB
  Channel 6: IN -8 dB OUT  +1 dB
  Channel 7: IN -8 dB OUT  +1 dB
  Channel 8: IN -8 dB OUT  +1 dB


Defaults For Pro Audio: +4dBu and Consumer Audio: -10dBV
--------------------------------------------------------

When running **glucid** you may have noticed the message: ::

  Analog Gain:
  
  ***************************************
  Recommended: +4dBu: IN -8 dB OUT  +1 dB
              -10dBV: IN +4 dB OUT -11 dB
  ***************************************


**glucid** also provides options to easy use these recommended settings.


From the output of **glucid --help**: ::

    --set_gain=PRESET
	 set analog INPUTS and OUTPUT to recommended PRESET
        	PRESET is an integer value +4 or -10:
         	'+4' -Sets all INPUTS to -8dB and all OUTPUTS to +1dB
         	'-10' -Sets all INPUTS to +4dB and all OUTPUTS to -11dB

Why Are These Values Chosen?
----------------------------

From the original Lucid ADA8824 Manual, these settings provide approximately 20dB of dynamic range.

Setting Audio Level Defaults
----------------------------

Use **--set_gain=+4** for commercial gear and **--set_gain=-10** for consumer gear.

For example: ::

  $ glucid --set_gain=-10

Will result in: ::

  Channel 1: IN +4 dB OUT  -11dB
  Channel 2: IN +4 dB OUT  -11dB
  Channel 3: IN +4 dB OUT  -11dB
  Channel 4: IN +4 dB OUT  -11dB
  Channel 5: IN +4 dB OUT  -11dB
  Channel 6: IN +4 dB OUT  -11dB
  Channel 7: IN +4 dB OUT  -11dB
  Channel 8: IN +4 dB OUT  -11dB

And: ::

  $ glucid --set_gain=+4

Will result in::
  
  Channel 1: IN -8 dB OUT  +1 dB
  Channel 2: IN -8 dB OUT  +1 dB
  Channel 3: IN -8 dB OUT  +1 dB
  Channel 4: IN -8 dB OUT  +1 dB
  Channel 5: IN -8 dB OUT  +1 dB
  Channel 6: IN -8 dB OUT  +1 dB
  Channel 7: IN -8 dB OUT  +1 dB
  Channel 8: IN -8 dB OUT  +1 dB


Setting Levels on Individual Channels
-------------------------------------

Channel Levels can also be set individually.   

From **glucid --help**: ::
    
  --sci,--set_channel_input_gain=GAIN CHANNEL [CHANNEL...] 
	         set analog INPUT gain of CHANNELs to GAIN
        	GAIN is an integer value between -95 and +32
        	CHANNELs are integer values between 1-8:
         		1-8 -'INPUT Channels 1-8'

  --sco,--set_channel_output_gain=GAIN CHANNEL [CHANNEL...] 
	         set analog OUTPUT gain of CHANNELs to GAIN
        	GAIN - an integer value between -95 and +32
        	CHANNELs - integer values between 1-8:
         		1-8 -'OUTPUT Channels 1-8'

So, for example, if settings were currently: ::

  $ glucid --get_gain

  Channel 1: IN -8 dB OUT  +1 dB
  Channel 2: IN -8 dB OUT  +1 dB
  Channel 3: IN -8 dB OUT  +1 dB
  Channel 4: IN -8 dB OUT  +1 dB
  Channel 5: IN -8 dB OUT  +1 dB
  Channel 6: IN -8 dB OUT  +1 dB
  Channel 7: IN -8 dB OUT  +1 dB
  Channel 8: IN -8 dB OUT  +1 dB

Example: To set the channel input level on channels 1,2 and 4 to +5dB: ::
  
  $ glucid --sci=+5 1 2 4

  Channel 1: IN +5 dB OUT  +1 dB
  Channel 2: IN +5 dB OUT  +1 dB
  Channel 3: IN -8 dB OUT  +1 dB
  Channel 4: IN +5 dB OUT  +1 dB
  Channel 5: IN -8 dB OUT  +1 dB
  Channel 6: IN -8 dB OUT  +1 dB
  Channel 7: IN -8 dB OUT  +1 dB
  Channel 8: IN -8 dB OUT  +1 dB
  
Example: To set the channel output levels on channels 1,3,5 and 7 to -15dB: ::

  $ glucid --sco=-15 1 3 5 7 
  
  Channel 1: IN -8 dB OUT  -15dB
  Channel 2: IN -8 dB OUT  +1 dB
  Channel 3: IN -8 dB OUT  -15dB
  Channel 4: IN -8 dB OUT  +1 dB
  Channel 5: IN -8 dB OUT  -15dB
  Channel 6: IN -8 dB OUT  +1 dB
  Channel 7: IN -8 dB OUT  -15dB
  Channel 8: IN -8 dB OUT  +1 dB


Front LED Meters
================

Get Current Meter Source
------------------------

Use the **--get_meter** option: ::

  $ glucid --get_meter

  Meter:		Analog In


Set Meter Source
----------------

From **glucid --help**: ::

  --set_meter=METER	set meters to METER
        	METER is a number 0-3:
         	0 -'Analog In'
         	1 -'Digital In'
         	2 -'Analog Out'
         	3 -'Digital Out'

For example: ::

  $  glucid --set_meter=3
  Meter:		Digital Out



Clock Sync
==========

Get Current Sync Source
-----------------------

Use the **--get_sync** option: ::

  $ glucid --get_sync

  Sync:		WordClock

Set Sync Source
---------------

From **glucid --help**: ::

  --set_sync=SYNC	set source to sync to SYNC
        	SYNC is a number 0-7:
         	0 -'ADAT'
         	1 -'WordClock'
         	2 -'44.1 internal'
         	3 -'48 Internal'
         	4 -'AES In1'
         	5 -'AES In2'
         	6 -'AES In3'
         	7 -'S/PDIF In'
  
For example: ::

  $  glucid --set_sync=0

  Sync:		ADAT

Analog Out Source
=================

The Lucid 8824 can convert digital audio to analog audio sourced from the ADAT or AES interconnects.

Get Current Analog Out Source
-----------------------------

Use the **--get_analog** option: ::

  $  glucid --get_analog

  Analog Source:	ADAT In


Set Analog Out Source
---------------------

From **glucid --help**: ::

    --set_analog=SRC	set analog output source to SRC
        	SRC is a number 0 or 1:
         	0 -'ADAT In'
         	1 -'AES In'

For example: ::

  $  glucid --set_analog=1

  Analog Source:	AES In

ADAT Out (Optical) Source
=========================

The Lucid 8824 can send digital audio via it's ADAT (optical) connector sourced from either Analog or AES inputs

Get Current ADAT Out (Optical) Source
-------------------------------------

Use the **--get_opt** option: ::

  $  glucid --get_opt

  Optical Source:	Analog In


Set ADAT Out Source
---------------------

From **glucid --help**: ::

  --set_opt=SRC	set optical output source to SRC
        	SRC is a number 0 or 1:
         	0 -'Analog In'
         	1 -'AES In'


For example: ::

  $  glucid --set_opt=1

  Optical Source:	AES In

  
  
Digital Input Channels 1 and 2 (S/PDIF)
=======================================

If you wish to use the S/PDIF Input connection on the Lucid 8824, you must set Digital Channels 1,2 to 'S/PDIF', otherwise audio will be sourced from AES Channels 1 and 2.



Get Current Input for Digital Channels 1 and 2
----------------------------------------------

Use the **--get_dig1** option: ::

  $  glucid --get_dig1

  Dig Input 1,2:	AES

Set Input for Digital Channels 1 and 2
--------------------------------------

From **glucid --help**: ::

  --set_dig1=DIGIN	set digital inputs 1,2 to DIGIN
        	DIGIN is 0 or 1:
         	0 -'AES 1,2'
         	1 -'S/PDIF'


For example: ::

  $  glucid --set_dig1=1

  Dig Input 1,2:	S/PDIF
