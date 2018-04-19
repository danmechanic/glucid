===============================
**glucid** Python Documentation
===============================

**glucid** is a software package that provides a **glucid8824** module which provides a Command Line Interface and api as well as a **Glucid8824** class that represents an instance of a Lucid ADA8824


Confirm the **glucid8824** module can be imported
-------------------------------------------------

Within a Python3 interpreter, you may import he **glucid8824** module: ::
  
  >>> from glucid import glucid8824

Simple Example Setting Clock Sync Using Python
==============================================

First, import glucid

.. code-block:: Python

   >>> import glucid.glucid8824 as glucid

Create a new Glucid8824 object, by default this uses /dev/ttyUSB0

.. code-block:: Python

   >>> mylucid = glucid.Glucid8824()

We connect to our ADA8824

.. code-block:: Python

   >>> mylucid.connect()
   True

Check the current clock sync source

.. code-block:: Python

   >>> mylucid.get_sync_source()
   'ADAT'

Set the clock sync to WordClock

.. code-block:: Python

   >>> mylucid.set_sync_source(1)
   >>> mylucid.get_sync_source()
   'WordClock'


  
**glucid8824** Module Documentation
===================================


.. automodule:: glucid.glucid8824
   :members: get_all, get_aes_src, get_analog_src, set_analog_src, get_opt_src, set_opt_src, get_meter, set_meter, get_sync, set_sync, get_dig1, set_dig1, get_gain, set_gain_channels, main

**Glucid8824** Class Documentation
----------------------------------


.. autoclass:: glucid.glucid8824.Glucid8824
   :members:
   :special-members:
      
