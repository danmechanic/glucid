=========================
**xglucid** GUI Interface
=========================

.. image::  ./xglucid.png

.. note::
   xglucid requires PyQt5 as well as Python 3
   
.. note::

   The user who is running glucid must be able to read
   and write to whichever serial device you are using; consult your
   operating system documentation.


First:

* Power Off your Lucid 8824
* Flip DIP Switch 1 on your Lucid 8824 to **down**  (remote)
* Connect a 9 pin Serial connector from the Lucid 8824 to your computer
* Power On your Lucid 8824

Know what Serial Port you are Using
===================================

The default is /dev/ttyUSB0
---------------------------

By default, **glucid** assumes you are using **/dev/ttyUSB0**   Use the pulldown
menu to the left to select your Serial interface

Select **READ**
---------------

This will read all values from your ADA8824 and enable the options with
the values currently stored on your unit.

Write all Values wtih **WRITE**
-------------------------------

If you change any values, select **WRITE** to write them to your ADA8824.

**xglucid** will read the values again and set the interface accordingly.