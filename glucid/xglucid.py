#!/usr/bin/env python3
"""
xglucid is a part of the glucid package and provides 
a qt Graphical interface to configure a Lucid 8824 
Analog/Digital Audio Converter RS232 interface over 
a serial port.

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
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QToolTip, QMessageBox, QGridLayout, QVBoxLayout,
                             QCheckBox, QHBoxLayout, QSlider, QLabel,
                             QSplashScreen)
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QPixmap
import sys
import os
from time import sleep
import glucid.Glucid8824_UI
import glucid.glucid8824 as glucid8824
import configparser
import serial.tools.list_ports as lsports

CLEAN_NONEX_DEVICES=True

class xglucid(QtWidgets.QMainWindow, glucid.Glucid8824_UI.Ui_MainWindow):
    """xglucid is just a class to call the Qt MainWindow"""
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        # load the default device from conf file
        currentdevice = glucid8824.Glucid8824.get_device_from_cfg()
        self.SerialPortCombo.setCurrentText(currentdevice)
        self.connection_label.setText(
            glucid8824.Glucid8824.rs232_or_midi(currentdevice))

        # cleanup non-valid serial ports
        # from interface...
        # first build a list of the ports
        portlist = []
        allports = []

        #print("BEFORE: all devices:")
        for i in range(self.SerialPortCombo.count()):
            allports.append(self.SerialPortCombo.itemText(i))
        #print(allports)
                
        for i in lsports.comports():
            portlist.append(i.device)

        # pyserial doesn't recognize these
        # and we need them...
        portlist.append("/dev/tty.usbserial")

        # then remove the SerialPortCombo items that aren't there
        #print("On this system:")
        #print(portlist)
        #print("now stripping:")
        for i in allports:
            #print("examining: "+i)
            if i not in portlist:
                #print("removing: "+i)
                self.SerialPortCombo.removeItem(
                    self.SerialPortCombo.findText(i))

                
        
def main():
    """call QApplication"""
    app = QApplication(sys.argv)
    splashmap = QPixmap(":/newPrefix/glucidSplash.png")
    splash = QSplashScreen(splashmap, QtCore.Qt.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage("<h1>Make sure dip switch 1 is down on your lucid</h1>")
    app.processEvents()
    timer = QtCore.QElapsedTimer()
    timer.start()

    while timer.elapsed() < 4000 :
        app.processEvents()


    form = xglucid()
    form.show()

    splash.finish(form)
    app.exec_()

# if we wish to run from CLI without package
if __name__ == '__main__':
    main()
