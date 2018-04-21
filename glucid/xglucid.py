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
                             QCheckBox, QHBoxLayout, QSlider, QLabel)
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon
import sys
import glucid.Glucid8824_UI


class xglucid(QtWidgets.QMainWindow, glucid.Glucid8824_UI.Ui_MainWindow):
    """xglucid is just a class to call the Qt MainWindow"""
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)


def main():
    """call QApplication"""
    app = QApplication(sys.argv)
    form = xglucid()
    form.show()
    app.exec_()

# if we wish to run from CLI without package
if __name__ == '__main__':
    main()
