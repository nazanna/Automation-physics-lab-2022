import os
import sys
import serial
import csv
import time
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication,
                             QLineEdit,
                             QPushButton,
                             QWidget,
                             QGridLayout,
                             QTableWidgetItem,
                             QHeaderView,
                             QLabel
                             )
from Abstract_window import AbstractWindow
from Main_experiment_window import (MainExperimentDataWindow,
                                    MainExperimentChartWindow)
from GraduationWindow import GraduationWindow
from SignWindow import SignWindow
from ResistanceWindow import ResistanceWindow


class Start:
    def __init__(self):
        self.number = 0
        self.foldername = None
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        self.window = StartWindow(self)
        
        # self.add_ser()
        # self.parent.amp_name= os.path.join('/dev', 'usbtmc1')
        # self.volt_name = os.path.join('/dev', 'usbtmc0')
        
        self.draw()
        self.app.exec()

    def draw(self):
        self.window.show()

    def change_number(self):
        if self.number == 0:
            self.window.close()
            self.window = StartWindow(self)
        if self.number == 10:
            self.window.close()
            self.window = GraduationWindow(self)
        if self.number == 20:
            self.window.close()
            self.window = MainExperimentDataWindow(self)
        if self.number == 21:
            self.window.close()
            self.window = MainExperimentChartWindow(self)
        if self.number == 30:
            self.window.close()
            self.window = SignWindow(self)
        if self.number == 40:
            self.window.close()
            self.window = ResistanceWindow(self)
        self.draw()
        
    def add_ser(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB2',
            baudrate=9600,
            timeout=1
        )
        self.ser.isOpen()
        msg = 'OUTput on\n'
        self.ser.write(msg.encode('ascii'))


class StartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Эффект Холла в полупроводниках')
        self.parent = parent
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        if not self.parent.foldername:
            self.lineEdit = QLineEdit(placeholderText='Введите фамилию')
        else:
            self.lineEdit = QLineEdit(placeholderText=self.parent.foldername)
        self.lineEdit.returnPressed.connect(self.enter_name)

        self.flow = QPushButton('Градуировка электромагнита')
        self.flow.clicked.connect(self.flow_click)
        if not self.parent.foldername:
            self.flow.setEnabled(False)
            
        self.sign = QPushButton('Знак носителей')
        self.sign.clicked.connect(self.sign_click)
        if not self.parent.foldername:
            self.sign.setEnabled(False)
            
        self.res = QPushButton('Удельная проводимость')
        self.res.clicked.connect(self.res_click)
        if not self.parent.foldername:
            self.res.setEnabled(False)
                       
        self.main = QPushButton('Основной эксперимент')
        self.main.clicked.connect(self.main_click)
        if not self.parent.foldername:
            self.main.setEnabled(False)
        if self.parent.foldername:
            self.lineEdit.setReadOnly(True)
            
        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.setRowStretch(1, 1)
        self.hbox_layout.addWidget(self.lineEdit, 1, 0, 1, 2)
        self.hbox_layout.addWidget(self.flow, 2, 0)
        self.hbox_layout.addWidget(self.sign, 3, 0)
        self.hbox_layout.addWidget(self.res, 3, 1)
        self.hbox_layout.addWidget(self.main, 2, 1)

    def flow_click(self):
        self.parent.number = 10
        self.parent.change_number()

    def main_click(self):
        self.parent.number = 20
        self.parent.change_number()
        
    def res_click(self):
        self.parent.number = 40
        self.parent.change_number()
        
    def sign_click(self):
        self.parent.number = 30
        self.parent.change_number()

    def enter_name(self):
        # make folder
        self.parent.foldername = self.lineEdit.text()
        self.parent.folder = os.path.join(os.getcwd(), self.parent.foldername)
        if not os.path.exists(self.parent.folder):
            os.mkdir(self.parent.folder)

        self.flow.setEnabled(True)
        self.main.setEnabled(True)
        self.sign.setEnabled(True)
        self.res.setEnabled(True)
        self.lineEdit.setReadOnly(True)


    


start = Start()

# import time
# import serial

# ser=serial.Serial(
#     port='/dev/ttyUSB2',
#     baudrate=9600,
#     timeout=1
# )
# ser.isOpen()
# msg='Output on\n'

# ser.write(msg.encode('ascii'))


# msg='VOLTage 1\n'
# ser.write(msg.encode('ascii'))

# while 1:

#         msg='READ?\n'
#         ser.write(msg.encode('ascii'))
#         time.sleep(1)

#         bytesToRead=ser.inWaiting()
#         data=ser.read(bytesToRead)
#         print(data)
