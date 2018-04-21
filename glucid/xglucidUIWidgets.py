"""
@author Dan Mechanic (dan.mechanic@gmail.com)

"""


from PyQt5.QtWidgets import QWidget, QLabel, QSlider, QComboBox, QCheckBox, QPushButton
from PyQt5.QtGui import QPainter, QColor, QFont
import glucid.xglucidUIWidgets


#import Lucid8824
import glucid.glucid8824 as glucid

class xglucidWidget(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        #self.parent().statusBar().showMessage("Dan Mechanic whut whut")
        QWidget.__init__(self, parent)

        # TODO: read user's previous serial port setting
        #self.lucid = Lucid8824.Lucid8824()
        self.InputSliders = []
        self.OutputSliders = []
        self.myLucid = glucid.Glucid8824();
        self.initUI()

    def initUI(self):      
        self.text = "Dan"
        self.setGeometry(0, 0, 897, 471)
        self.setWindowTitle('Drawing text')

        self.show()


        if not self.myLucid.connect():
            self.parent().statusBar().showMessage(
                'Cannot connect to lucid using %s'%self.myLucid.get_iface());

    def need_write_status(self):
        self.parent().statusBar().showMessage('Need to Write to the Device')

    def make_sliders(self):
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
        

    def on_glucid_slider_changed(self,value):
        changed_slider = self.sender()
        self.make_sliders()

        if changed_slider in self.InputSliders and self.parent().LinkInCh.isChecked():
            for sl in self.InputSliders:
                if sl is not changed_slider:
                    sl.setValue(value)
        if changed_slider in self.OutputSliders and self.parent().LinkOutCh.isChecked():
            for sl in self.OutputSliders:
                if sl is not changed_slider:
                    sl.setValue(value)


    def on_serial_port_changed(self,value):
        # TODO: implement set_iface in glucid? this is kind of crummy...
        self.myLucid = glucid.Glucid8824(siface=value)
        
    def disable_all_except_comm(self):
        DontDisable = [
            "SerialPortCombo",
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
        for i in self.parent().centralwidget.children():
            i.setEnabled(True)

    def read_button_clicked(self):
        """The read button was clicked, if successful set all
        widgets to proper values, otherwise reflect the failure
        in the status bar
        """
        if self.myLucid.connect():
            self.parent().statusBar().showMessage("Connected using %s"%
                                                  self.myLucid.get_iface())
            self.set_ui_from_lucid()
        else:
            self.parent().statusBar().showMessage("FAILED to connect using %s"%
                                                  self.myLucid.get_iface())


    def set_ui_from_lucid(self):
        """Given we are connected to a lucid, set all UI values"""

        self.disable_all_except_comm()

        if self.myLucid.connect():
            self.parent().statusBar().showMessage("Connected using %s and reading DATA..."%
                                                  self.myLucid.get_iface())
        else:
            return -1
        


        ## Set Clock Sync
        self.parent().statusBar().showMessage("Connected using %s and reading Clock Sync..."%
                                            self.myLucid.get_iface())

        self.parent().centralwidget.findChild(QComboBox,"LucidSyncCombo").setCurrentIndex(
            self.myLucid.get_sync_source(False)[0])
        self.parent().centralwidget.findChild(QComboBox,"LucidSyncCombo").setEnabled(True)

        ## set Metering
        self.parent().statusBar().showMessage("Connected using %s and reading Front Meter..."%
                                            self.myLucid.get_iface())

        self.parent().centralwidget.findChild(QComboBox,"LucidMeterCombo").setCurrentIndex(
            self.myLucid.get_meter(False))
        self.parent().centralwidget.findChild(QComboBox,"LucidMeterCombo").setEnabled(True)

        ## set optical out
        self.parent().statusBar().showMessage("Connected using %s and reading ADAT OUT source..."%
                                            self.myLucid.get_iface())

        self.parent().centralwidget.findChild(QComboBox,"LucidOpticalCombo").setCurrentIndex(
            self.myLucid.get_opt_source(False)[0])
        self.parent().centralwidget.findChild(QComboBox,"LucidOpticalCombo").setEnabled(True)

        ## set AES out
        ## NOTE: SETTING AES DOES NOT APPEAR TO WORK
        self.parent().statusBar().showMessage(
            "Connected using %s and reading AES OUT source... WARNING: READ-ONLY Value"%
                                            self.myLucid.get_iface())



        self.parent().centralwidget.findChild(QComboBox,"LucidOpticalCombo").setCurrentIndex(
            self.myLucid.get_opt_source(False)[0])

        ## Leave disabled because you cannot set this BUG
        ## self.parent().centralwidget.findChild(QComboBox,
        ##                            "LucidOpticalCombo").setEnabled(True)

        ## set anlog out src
        self.parent().statusBar().showMessage("Connected using %s and reading Analog OUT source..."%
                                            self.myLucid.get_iface())
        self.parent().centralwidget.findChild(QComboBox, "LucidAnalogSrcCombo").setCurrentIndex(
            self.myLucid.get_analog_source(False)[0])
        self.parent().centralwidget.findChild(QComboBox, "LucidAnalogSrcCombo").setEnabled(True)

        ## set digital in 1,2
        self.parent().statusBar().showMessage("Connected using %s and reading Digital Ch 1,2 source..."%
                                            self.myLucid.get_iface())

        self.parent().centralwidget.findChild(QComboBox, "LucidSpdifCombo").setCurrentIndex(
            self.myLucid.get_dig1(False))
        self.parent().centralwidget.findChild(QComboBox, "LucidSpdifCombo").setEnabled(True)

        ## set deviceId
        self.parent().statusBar().showMessage("Connected using %s and reading DEVICE ID..."%
                                              self.myLucid.get_iface())

        self.parent().centralwidget.findChild(QComboBox, "LucidIdCombo").setCurrentIndex(
            int(self.myLucid.get_instanceid()))

        ## Leave disabled, no way to set
        ## self.parent().centralwidget.findChild(QComboBox, "LucidIdCombo").setEnabled(True)

        ## set input and output sliders
        self.parent().statusBar().showMessage("Connected using %s and reading Channel Levels..."%
                                            self.myLucid.get_iface())

        gainlist = self.myLucid.get_gain()
        self.make_sliders()
        
        self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").setCheckState(False)
        self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").setCheckState(False)
        for i in range(0,8):
            self.parent().centralwidget.findChild(QSlider, "SliderIN_%s"% str(i + 1)).setEnabled(True)
            self.parent().centralwidget.findChild(QSlider, "SliderOUT_%s"% str(i + 1)).setEnabled(True)
            instr="SliderIN_"+str(i+1)
            outstr="SliderOUT_"+str(i+1)

            ## hack to get all labels to redraw no matter previous val
            ## wont work if previous value was -95... ok... that's silent
            self.parent().centralwidget.findChild(QSlider, instr).setValue(
                -95)
            self.parent().centralwidget.findChild(QSlider, outstr).setValue(
                -95)
            # set to gainlist values
            self.parent().centralwidget.findChild(QSlider, instr).setValue(
                int(gainlist[i]))
            self.parent().centralwidget.findChild(QSlider, outstr).setValue(
                int(gainlist[i+8]))
                        
        ## turn on other buttons...
        self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").setEnabled(True)
        self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").setEnabled(True)
        self.parent().centralwidget.findChild(QPushButton, "ProINButton").setEnabled(True)
        self.parent().centralwidget.findChild(QPushButton, "ProOUTButton").setEnabled(True)
        self.parent().centralwidget.findChild(QPushButton, "ConINButton").setEnabled(True)
        self.parent().centralwidget.findChild(QPushButton, "ConOUTButton").setEnabled(True)
        self.parent().centralwidget.findChild(QPushButton, "LucidWriteButton").setEnabled(True)


        
        self.parent().statusBar().showMessage("Finished Reading DATA")


    def pro_or_consumer_clicked(self):
        """a slot to handle when a user clicks the +4 or -10 buttons"""
        ## There's a bug here
        ## if the first Slider is already the correct
        ## value, no update is triggered.
        ## This should be reimplemented in the slider class
        ## so that sliders themselves have a slot that listens
        ## to the buttons signal.
        if self.sender().objectName() == "ProOUTButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderOUT_1").setValue(1)
        elif self.sender().objectName() == "ConOUTButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderOUT_1").setValue(-11)
        elif self.sender().objectName() == "ProINButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderIN_1").setValue(-8)
        elif self.sender().objectName() == "ConINButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderIN_1").setValue(4)

    def write_ui_to_lucid(self):
        """Given we are connected to a lucid, write all UI values to it"""
        self.disable_all_except_comm()

        if self.myLucid.connect():
            self.parent().statusBar().showMessage("Connected using %s and writing DATA..."%
                                                  self.myLucid.get_iface())
        else:
            return -1

        ## Set Clock Sync
        self.parent().statusBar().showMessage("Connected using %s and writing Clock Sync..."%
                                            self.myLucid.get_iface())
        self.myLucid.set_sync_source(
            self.parent().centralwidget.findChild(QComboBox,"LucidSyncCombo").currentIndex())
        
        ## set Metering
        self.parent().statusBar().showMessage("Connected using %s and writing Front Meter..."%
                                            self.myLucid.get_iface())
        self.myLucid.set_meter(
            self.parent().centralwidget.findChild(QComboBox,"LucidMeterCombo").currentIndex())


        ## set optical out
        self.parent().statusBar().showMessage("Connected using %s and writing ADAT OUT source..."%
                                            self.myLucid.get_iface())
        self.myLucid.set_opt_src(
            self.parent().centralwidget.findChild(QComboBox,"LucidOpticalCombo").currentIndex())

        ## set AES out
        ## NOTE: SETTING AES DOES NOT APPEAR TO WORK
        ##

        ## set anlog out src
        self.parent().statusBar().showMessage("Connected using %s and writing Analog OUT source..."%
                                            self.myLucid.get_iface())
        self.myLucid.set_analog_src(
            self.parent().centralwidget.findChild(QComboBox, "LucidAnalogSrcCombo").currentIndex())

        ## set digital in 1,2
        self.parent().statusBar().showMessage(
            "Connected using %s and writing Digital Ch 1,2 source..."%
            self.myLucid.get_iface())

        self.myLucid.set_dig1(
            self.parent().centralwidget.findChild(QComboBox, "LucidSpdifCombo").currentIndex())
        
        ## set deviceId
        ## no

        ## set input and output sliders
        self.parent().statusBar().showMessage("Connected using %s and writing Channel Levels..."%
                                            self.myLucid.get_iface())

        for i in range(1,9):
            self.myLucid.update_channel_in_gainlist(
                self.parent().centralwidget.findChild(QSlider,"SliderIN_"+str(i)).value(),i-1
            )
            self.myLucid.update_channel_in_gainlist(
                self.parent().centralwidget.findChild(QSlider,"SliderOUT_"+str(i)).value(),i+7
            )

            
        self.myLucid.write_gainlist_to_lucid()

        self.parent().statusBar().showMessage("Finished Writing DATA")
        self.set_ui_from_lucid()

    def pro_or_consumer_clicked(self):
        """a slot to handle when a user clicks the +4 or -10 buttons"""
        if self.sender().objectName() == "ProOUTButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderOUT_1").setValue(1)
        elif self.sender().objectName() == "ConOUTButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkOutCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderOUT_1").setValue(-11)
        elif self.sender().objectName() == "ProINButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderIN_1").setValue(-8)
        elif self.sender().objectName() == "ConINButton":
            self.parent().centralwidget.findChild(QCheckBox, "LinkInCh").setCheckState(True)
            self.parent().centralwidget.findChild(QSlider, "SliderIN_1").setValue(4)
            
    def write_button_clicked(self):
        """The write button was clicked, if successful set all
        widgets to proper values, otherwise reflect the failure
        in the status bar
        """
        self.disable_all_except_comm()

        ##
        if self.myLucid.connect():
            self.parent().statusBar().showMessage("Connected using %s"%
                                                  self.myLucid.get_iface())
            self.write_ui_to_lucid()
        else:
            self.parent().statusBar().showMessage("FAILED to connect using %s"%
                                                  self.myLucid.get_iface())

        
class xglucidLabel(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)

    def on_slider_value_changed(self, value):
        """setText with the value of `value` with
        positive values preceded with a `+` and 
        ended with `dB`
        """
        
        if self.sender().value() > 0:
            retstring=str('+'+str(self.sender().value())+"dB")
            self.setText(retstring)
        else:
            self.setText(str(self.sender().value())+"dB")

        
class xglucidInputSlider(QSlider):
    def __init__(self,parent=None):
        super().__init__(parent)
        
    def on_input_slider_value_changed(self, value):
        
        if self.sender().value() > 0:
            retstring=str('+'+str(self.sender().value())+"dB")
            self.setText(retstring)
        else:
            self.setText(str(self.sender().value())+"dB")