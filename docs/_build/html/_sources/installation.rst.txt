============
Installation
============

Requirements
============
**glucid** requires python >= 3, PySerial and:

* a serial port connected to a Lucid ADA8824 rs232 interface


.. figure:: FTDI_USB_SERIAL.jpg
   :scale: 25 %
   :alt: Usb - Serial 9-Pin Converter

   By default, **glucid** assumes you are using a USB to 9-pin serial adapter on linux and defaults to **/dev/ttyUSB0** , to overide this default, use the **-d** option.  Windows users may try **COM1** while OSX users may try **/dev/tty.usbserial**


Installing glucid via pip
=========================

glucid can installed via pip

.. code-block:: bash
		
   pip install glucid

   
Installing the latest version of glucid via git
===============================================

You can clone the latest version of glucid via:

.. code-block:: bash

	git clone https://github.com/danmechanic/glucid.git

And then install from the cloned source via:

.. code-block:: bash

	cd glucid/
	pip install -e .

Verifying correct installation
------------------------------

Within a terminal, you can first verify basic installation with:

.. code-block:: bash

   glucid --help

You can launch the GUI interface with:

.. code-block:: bash

   xglucid
   
In your Python distribution you may try to import the **glucid8824** module:

.. code-block:: Python

   from glucid import glucid8824 as glucid

   
		

