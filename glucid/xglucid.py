from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QToolTip, QMessageBox, QGridLayout, QVBoxLayout,
                             QCheckBox, QHBoxLayout, QSlider, QLabel)
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon

import sys # We need sys so that we can pass argv to QApplication

import Glucid8824_UI # This file holds our MainWindow and all design related things
              # it also keeps events etc that we defined in Qt Designer

class xglucid(QtWidgets.QMainWindow, Glucid8824_UI.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined


def main():
    app = QApplication(sys.argv)        # A new instance of QApplication
    form = xglucid()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app

if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                              # run the main function
