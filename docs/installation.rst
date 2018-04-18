============
Installation
============

Requirements
============
**glucid** requires python >= 3 and:

* a serial port connected to a Lucid 8824 rs232 interface

glucid assumes you are using a USB to 9-pin serial adapter
on linux and defaults to /dev/ttyUSB0

Easy installation of glucid
===========================

You can just clone the latest stable version of glucid via:

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

