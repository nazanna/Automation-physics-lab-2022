import os
import sys
import serial
import csv
import time
# from PyQt import KeepAspectRatioByExpanding
from PyQt6.QtGui import QIcon, QPalette, QImage, QBrush
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
from Main_experiment_window import MainWindow
from ChartWindow import ChartWindow
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
        
        self.add_equip()
        
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
            self.window = MainWindow(self)
        if self.number == 30:
            self.window.close()
            self.window = SignWindow(self)
        if self.number == 40:
            self.window.close()
            self.window = ResistanceWindow(self)
        if self.number == 50:
            self.window.close()
            self.window = ChartWindow(self)
        self.draw()
        
    def add_equip(self):
        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            timeout=1
        )
        self.ser.isOpen()
        msg = 'OUTput on\n'
        self.ser.write(msg.encode('ascii'))
        
        for i in range(3):
            l = 'usbtmc'+str(i)
            file = os.path.join('/dev', l)
            f = open(file, 'w')
            f.write('*IDN?\n')
            f.close()
            f = open(file, 'r')
            st = f.read(35)
            # print(st)
            f.close()
            if st=='AKIP,AKIP-2101/2,NDM36GBD4R0065,3.0':
                self.I_M_name =  os.path.join('/dev', l)
            
            if st=='AKIP,AKIP-2101/2,NDM36GBD4R0064,3.0':
                self.amp_name =  os.path.join('/dev', l)
            
            if st=='Prist,V7-78/1,TW00023291,03.31-01-0':
                self.volt_name =  os.path.join('/dev', l)
    
    
    def close(self):
        
        msg = 'VOLTage '+str(0)+'\n'
        self.ser.write(msg.encode('ascii'))
        
    def __del__(self):
        
        msg = 'OUTput off\n'
        self.ser.write(msg.encode('ascii'))
                    
            
        


class StartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Эффект Холла в полупроводниках')
        
        # palette = QPalette()
        # img = QImage('image.jpg')
        # scaled = img.scaled(self.size(), KeepAspectRatioByExpanding)
        # palette.setBrush(QPalette.Window, QBrush(scaled))
        # self.setPalette(palette)
        
        # self.setStyleSheet('.QWidget {background-image: url(style.jpg);}') 
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
            
        self.chart = QPushButton('Обработка данных')
        self.chart.clicked.connect(self.chart_click)
        if not self.parent.foldername:
            self.chart.setEnabled(False)
                       
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
        self.hbox_layout.addWidget(self.chart, 4, 0, 1, -1)

    def flow_click(self):
        self.parent.number = 10
        self.parent.change_number()
        
    def chart_click(self):
        self.parent.number = 50
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
        self.chart.setEnabled(True)
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
