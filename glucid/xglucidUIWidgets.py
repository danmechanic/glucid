"""xglucidUIWidgets provides custom classes for QtWidget
behavoir in glucid

xglucid is a part of the glucid package and provides
a qt Grpahical interface to configure a Lucid 8824
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
import glucid.xglucidUIWidgets
import glucid.glucid8824 as glucid
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import (QWidget, QLabel, QSlider, QComboBox,
                             QCheckBox, QPushButton)

class xglucidWidget(QWidget):
    """xglucidWidget extends QWidget to provide custom signals
    and slots fo the glucid interface
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        QWidget.__init__(self, parent)

        self.InputSliders = []
        self.OutputSliders = []

        self.myLucid = glucid.Glucid8824()
        self.myLucid.set_device_from_configfile()
        self.initUI()
        
    def initUI(self):
        """set geometry and title, call show()"""
        self.setGeometry(0, 0, 897, 471)
        self.setWindowTitle('xglucid')
        self.show()
        # update device selector
        


    def need_write_status(self):
        """Deprecated: `Needs write` written to status bar"""
        self.parent().statusBar().showMessage('Need to Write to the Device')

    def make_sliders(self):
        """Build lists `InputSliders` and `OutputSliders`.  This is
        a convenience function so these sliders can be linked together
        """
        self.InputSliders = [
            self.parent().SliderIN_1,
            self.parent().SliderIN_2,
            self.parent().SliderIN_3,
            self.parent().SliderIN_4,
            self.parent().SliderIN_5,
            self.parent().SliderIN_6,
            self.parent().SliderIN_7,
            self.parent().SliderIN_8,
        ]
        self.OutputSliders = [
            self.parent().SliderOUT_1,
            self.parent().SliderOUT_2,
            self.parent().SliderOUT_3,
            self.parent().SliderOUT_4,
            self.parent().SliderOUT_5,
            self.parent().SliderOUT_6,
            self.parent().SliderOUT_7,
            self.parent().SliderOUT_8,
        ]

    def on_glucid_slider_changed(self, value):
        """when a slider is changed, we check
        if the linked box is checked, and if so
        we set the values of other sliders...

        this may be better in a slider class
        as a slot routine...
        """
        
        changed_slider = self.sender()
        self.make_sliders()

        if (changed_slider in self.InputSliders and
            self.parent().LinkInCh.isChecked()):
            for sl in self.InputSliders:
                if sl is not changed_slider:
                    sl.setValue(value)
        if (changed_slider in self.OutputSliders and
        self.parent().LinkOutCh.isChecked()):
            for sl in self.OutputSliders:
                if sl is not changed_slider:
                    sl.setValue(value)

    def on_serial_port_changed(self, value):
        """Declare a new Glucid8824 object with the 
        new serial interface
        """
        # TODO: implement set_iface in glucid?
        self.myLucid = glucid.Glucid8824(siface=value)
        self.parent().connection_label.setText(
            glucid.Glucid8824.rs232_or_midi(value))
        self.disable_all_except_comm()

    def on_device_id_changed(self, value):
        """Update device_id """
        self.myLucid.LucidID = value
        self.disable_all_except_comm()
        
    def disable_all_except_comm(self):
        DontDisable = [
            "SerialPortCombo",
            "LucidIdCombo",
            "LucidReadButton",
            "labelIN_1",
            "labelIN_2",
            "labelIN_3",
            "labelIN_4",
            "labelIN_5",
            "labelIN_6",
            "labelIN_7",
            "labelIN_8",
            "labelOUT_1",
            "labelOUT_2",
            "labelOUT_3",
            "labelOUT_4",
            "labelOUT_5",
            "labelOUT_6",
            "labelOUT_7",
            "labelOUT_8",
        ]
        for i in self.parent().centralwidget.children():
                if i.objectName() not in DontDisable:
                    i.setEnabled(False)

    def enable_all_children(self):
        """Deprecated: delete this"""
        for i in self.parent().centralwidget.children():
            i.setEnabled(True)

    def read_button_clicked(self):
        """The read button was clicked, if successful set all
        widgets to proper values, otherwise reflect the failure
        in the status bar
        """
        try:
            if self.myLucid.connect():
                self.parent().statusBar().showMessage("Connected using %s" %
                                                      self.myLucid.get_iface())
                self.set_ui_from_lucid()
            else:
                self.parent().statusBar().showMessage(
                    "FAILED to connect using %s" %
                    self.myLucid.get_iface())
        except:
            self.parent().statusBar().showMessage("Connection FAILED: %s" %
                                                      self.myLucid.get_iface())
            self.disable_all_except_comm()
 
            
    def set_ui_from_lucid(self):
        """Given we are connected to a lucid, set all UI values 
        by reading each individually from the lucid, setting the
        widget value, and enabling the widget
        """

        self.disable_all_except_comm()
        # windows fails without disconnecting first
        self.myLucid.disconnect()
        if self.myLucid.connect():
            self.parent().statusBar().showMessage(
                "Connected using %s and reading DATA..." %
                self.myLucid.get_iface())
        else:
            return -1

        QCoreApplication.processEvents()
        # Set Clock Sync
        self.parent().statusBar().showMessage(
            "Connected using %s and reading Clock Sync..." %
            self.myLucid.get_iface())

        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidSyncCombo"
        ).setCurrentIndex(self.myLucid.get_sync_source(False))
        self.parent().centralwidget.findChild(
            QComboBox, "LucidSyncCombo"
        ).setEnabled(True)

        # set device_id
        self.parent().centralwidget.findChild(
            QComboBox, "LucidIdCombo"
        ).setCurrentIndex(int(self.myLucid.get_instanceid()))
        self.parent().centralwidget.findChild(
            QComboBox, "LucidIdCombo"
        ).setEnabled(True)

        # set Metering
        self.parent().statusBar().showMessage(
            "Connected using %s and reading Front Meter..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidMeterCombo"
        ).setCurrentIndex(self.myLucid.get_meter(False))
        self.parent().centralwidget.findChild(
            QComboBox, "LucidMeterCombo"
        ).setEnabled(True)
        QCoreApplication.processEvents()
        # set optical out
        self.parent().statusBar().showMessage(
            "Connected using %s and reading ADAT OUT source..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidOpticalCombo"
        ).setCurrentIndex(self.myLucid.get_opt_source(False))
        self.parent().centralwidget.findChild(
            QComboBox, "LucidOpticalCombo"
        ).setEnabled(True)

        # set AES out
        # NOTE: SETTING AES DOES NOT APPEAR TO WORK
        self.parent().statusBar().showMessage(
            "%s : reading AES OUT source... WARNING: READ-ONLY Value" %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidOpticalCombo"
        ).setCurrentIndex(self.myLucid.get_opt_source(False))
        # Leave disabled because you cannot set this BUG
        # self.parent().centralwidget.findChild(QComboBox,
        #                            "LucidOpticalCombo").setEnabled(True)

        # set anlog out src
        self.parent().statusBar().showMessage(
            "Connected using %s and reading Analog OUT source..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidAnalogSrcCombo"
        ).setCurrentIndex(self.myLucid.get_analog_source(False))
        self.parent().centralwidget.findChild(
            QComboBox, "LucidAnalogSrcCombo"
        ).setEnabled(True)

        # set digital in 1,2
        self.parent().statusBar().showMessage(
            "Connected using %s and reading Digital Ch 1,2 source..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidSpdifCombo"
        ).setCurrentIndex(self.myLucid.get_dig1(False))
        self.parent().centralwidget.findChild(
            QComboBox, "LucidSpdifCombo"
        ).setEnabled(True)

        # set deviceId
        self.parent().statusBar().showMessage(
            "Connected using %s and reading DEVICE ID..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.parent().centralwidget.findChild(
            QComboBox, "LucidIdCombo"
        ).setCurrentIndex(int(self.myLucid.get_instanceid()))

        self.parent().centralwidget.findChild(
            QComboBox, "LucidIdCombo").setEnabled(True)

        # set input and output sliders
        self.parent().statusBar().showMessage(
            "Connected using %s and reading Channel Levels..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        
        # turn on other buttons...
        self.parent().centralwidget.findChild(
            QCheckBox, "LinkInCh").setEnabled(True)
        self.parent().centralwidget.findChild(
            QCheckBox, "LinkOutCh").setEnabled(True)
        self.parent().centralwidget.findChild(
            QCheckBox, "LinkInCh").setCheckState(self.myLucid.is_in_linked())
        self.parent().centralwidget.findChild(
            QCheckBox, "LinkOutCh").setCheckState(self.myLucid.is_out_linked())

        self.myLucid.get_gain()
        self.make_sliders()
        
        for i in range(0, 8):
            instr = "SliderIN_"+str(i+1)
            outstr = "SliderOUT_"+str(i+1)

            self.parent().centralwidget.findChild(
                QSlider, instr).setEnabled(True)
            self.parent().centralwidget.findChild(
                QSlider, outstr).setEnabled(True)

            # hack to get all labels to redraw no matter previous val
            # wont work if previous value was -95... ok... that's silent
            self.parent().centralwidget.findChild(QSlider, instr).setValue(
                -95)
            self.parent().centralwidget.findChild(QSlider, outstr).setValue(
                -95)
            # set to gainlist values
            self.parent().centralwidget.findChild(QSlider, instr).setValue(
                int(self.myLucid.gainlist[i]-96))
            self.parent().centralwidget.findChild(QSlider, outstr).setValue(
                int(self.myLucid.gainlist[i+8]-96))



        self.parent().centralwidget.findChild(
            QPushButton, "ProINButton").setEnabled(True)
        self.parent().centralwidget.findChild(
            QPushButton, "ProOUTButton").setEnabled(True)
        self.parent().centralwidget.findChild(
            QPushButton, "ConINButton").setEnabled(True)
        self.parent().centralwidget.findChild(
            QPushButton, "ConOUTButton").setEnabled(True)
        self.parent().centralwidget.findChild(
            QPushButton, "LucidWriteButton").setEnabled(True)
        self.parent().statusBar().showMessage("Finished Reading DATA")
        QCoreApplication.processEvents()
        # windows fails without disconnecting first
        self.myLucid.disconnect()

        
    def pro_or_consumer_clicked(self):
        """a slot to handle when a user clicks the +4 or -10 buttons"""
        # There's a bug here
        # if the first Slider is already the correct
        # value, no update is triggered.
        # This should be reimplemented in the slider class
        # so that sliders themselves have a slot that listens
        # to the buttons signal.
        if self.sender().objectName() == "ProOUTButton":
            self.parent().centralwidget.findChild(
                QCheckBox, "LinkOutCh").setCheckState(True)
            self.parent().centralwidget.findChild(
                QSlider, "SliderOUT_1").setValue(1)
        elif self.sender().objectName() == "ConOUTButton":
            self.parent().centralwidget.findChild(
                QCheckBox, "LinkOutCh").setCheckState(True)
            self.parent().centralwidget.findChild(
                QSlider, "SliderOUT_1").setValue(-11)
        elif self.sender().objectName() == "ProINButton":
            self.parent().centralwidget.findChild(
                QCheckBox, "LinkInCh").setCheckState(True)
            self.parent().centralwidget.findChild(
                QSlider, "SliderIN_1").setValue(-8)
        elif self.sender().objectName() == "ConINButton":
            self.parent().centralwidget.findChild(
                QCheckBox, "LinkInCh").setCheckState(True)
            self.parent().centralwidget.findChild(
                QSlider, "SliderIN_1").setValue(4)

    def write_ui_to_lucid(self):
        """Given we are connected to a lucid, write all UI values to it
        
        We write all values, and not just updated ones because
        something may have changed on the unit since we last read them
        and writing what the user sees would be the most predictable 
        behavoir

        however, it's slow.
        """
        self.disable_all_except_comm()
        # windows fails without disconnecting first
        self.myLucid.disconnect()

        if self.myLucid.connect():
            self.parent().statusBar().showMessage(
                "Connected using %s id: %s and writing DATA..." %
                (self.myLucid.get_iface(),
                 self.myLucid.get_instanceid()) )
            QCoreApplication.processEvents()
            self.myLucid.glucidconf['DEFAULT']['Device']=self.myLucid.get_iface()
            self.myLucid.glucidconf['DEFAULT']['DEVICE_ID']=self.myLucid.get_instanceid()
        else:
            self.parent().statusBar().showMessage(
                "ERROR: Unable to connect to %s id %s to write DATA" %
                (self.myLucid.get_iface(),
                 self.myLucid.get_instancid()))            
            return -1
        
        
        # Set Clock Sync
        self.parent().statusBar().showMessage(
            "Connected using %s and writing Clock Sync..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.myLucid.set_sync_source(
            self.parent().centralwidget.findChild(
                QComboBox, "LucidSyncCombo").currentIndex())



        # # set Metering
        # self.parent().statusBar().showMessage(
        #     "Connected using %s and writing Front Meter..." %
        #     self.myLucid.get_iface())
        # self.myLucid.set_meter(
        #     self.parent().centralwidget.findChild(
        #         QComboBox, "LucidMeterCombo").currentIndex())

        # # set digital in 1,2
        # self.parent().statusBar().showMessage(
        #     "Connected using %s and writing Digital Ch 1,2 source..." %
        #     self.myLucid.get_iface())

        # self.myLucid.set_dig1(
        #     self.parent().centralwidget.findChild(
        #         QComboBox, "LucidSpdifCombo").currentIndex())

        ### Updated to use set_meter_and_dig1
        self.parent().statusBar().showMessage(
            "Connected using %s and writing mode..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.myLucid.set_meter_and_dig1(
            (4 * self.parent().centralwidget.findChild(
                QComboBox, "LucidSpdifCombo").currentIndex()) +
            self.parent().centralwidget.findChild(
                QComboBox, "LucidMeterCombo").currentIndex())
        
        # set optical out
        self.parent().statusBar().showMessage(
            "Connected using %s and writing ADAT OUT source..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.myLucid.set_opt_src(
            self.parent().centralwidget.findChild(
                QComboBox, "LucidOpticalCombo").currentIndex())

        # set AES out
        # NOTE: SETTING AES DOES NOT APPEAR TO WORK
        #

        # set anlog out src
        self.parent().statusBar().showMessage(
            "Connected using %s and writing Analog OUT source..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        self.myLucid.set_analog_src(
            self.parent().centralwidget.findChild(
                QComboBox, "LucidAnalogSrcCombo").currentIndex())


        # save state of sliders, if they are linked
        if self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").isChecked():
            self.myLucid.glucidconf['DEFAULT']['LINKINCH']='1'
        else:
            self.myLucid.glucidconf['DEFAULT']['LINKINCH']='0'

        if self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").isChecked():
            self.myLucid.glucidconf['DEFAULT']['LINKOUTCH']='1'
        else:
            self.myLucid.glucidconf['DEFAULT']['LINKOUTCH']='0'
            
            
        # set input and output sliders
        self.parent().statusBar().showMessage(
            "Connected using %s and writing Channel Levels..." %
            self.myLucid.get_iface())
        QCoreApplication.processEvents()
        for i in range(1, 9):
            self.myLucid.update_channel_in_gainlist(
                self.parent().centralwidget.findChild(
                    QSlider, "SliderIN_"+str(i)).value(), i-1
            )
            self.myLucid.update_channel_in_gainlist(
                self.parent().centralwidget.findChild(
                    QSlider, "SliderOUT_"+str(i)).value(), i+7
            )

        self.myLucid.write_gainlist_to_lucid()
        
        self.parent().statusBar().showMessage("Finished Writing DATA")
        QCoreApplication.processEvents()
        # windows fails without disconnecting first
        self.myLucid.disconnect()
        self.myLucid.write_configfile()
        
        self.set_ui_from_lucid()
        return 1

    def write_button_clicked(self):
        """The write button was clicked, if successful set all
        widgets to proper values, otherwise reflect the failure
        in the status bar
        """
        self.disable_all_except_comm()

        if self.myLucid.connect():
            self.parent().statusBar().showMessage("Connected using %s" %
                                                  self.myLucid.get_iface())
            if self.write_ui_to_lucid() < 0:
                self.parent().statusBar().showMessage("ERROR: Failed to write")
        else:
            self.parent().statusBar().showMessage("FAILED to connect using %s" %
                                                  self.myLucid.get_iface())


class xglucidLabel(QLabel):
    """A class to be used to label qglucid sliders"""
    
    def __init__(self, parent=None):
        super().__init__(parent)

    def on_slider_value_changed(self, value):
        """setText with the value of `value` with
        positive values preceded with a `+` and
        ended with `dB`
        """

        if self.sender().value() > 0:
            retstring = str('+'+str(self.sender().value())+"dB")
            self.setText(retstring)
        else:
            self.setText(str(self.sender().value())+"dB")
        QCoreApplication.processEvents()


class xglucidInputSlider(QSlider):
    """Not used;  something like this should be used for the
    linked channel behavoir
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def on_input_slider_value_changed(self, value):

        if self.sender().value() > 0:
            retstring = str('+'+str(self.sender().value())+"dB")
            self.setText(retstring)
        else:
            self.setText(str(self.sender().value())+"dB")
