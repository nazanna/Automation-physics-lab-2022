import os
import sys
# import serial
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
        self.current=0
        self.window = StartWindow(self)
        
        
        l = 'usbtmc'+str(1)
        self.I_M_name =  os.path.join('/dev', l)
        # self.add_equip()
        
        
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
            print(st, i)
            f.close()
            if st=='AKIP,AKIP-2101/2,NDM36GBD4R0065,3.0':
                self.amp_name =  os.path.join('/dev', l)
            
            if st=='AKIP,AKIP-2101/2,NDM36GBD4R0064,3.0':
                self.I_M_name =  os.path.join('/dev', l)
            
            if st=='Prist,V7-78/1,TW00023291,03.31-01-0':
                self.volt_name =  os.path.join('/dev', l)
    
    
    def close(self):
        pass
        msg = 'VOLTage '+str(0)+'\n'
        self.ser.write(msg.encode('ascii'))
        
    def __del__(self):
        pass
        msg = 'OUTput off\n'
        self.ser.write(msg.encode('ascii'))
        
        
        
                    
            
        


class StartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()
        
        self.setWindowTitle('Эффект Холла в полупроводниках')
        self.parent = parent
        self.parent.a = 2/10**3
        self.parent.l = 4/10**3
        self.parent.L = 5/10**3
        self.parent.sigma = 4469
        self.parent.dataname = 'data.csv'

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
        # if not self.parent.foldername or not self.parent.current==0:
        #     self.flow.setEnabled(False)
        self.flow_text = QLabel('Измеряется зависимость тока через электромагнит от магнитной индукции при помощи измерителя магнитной индукции', self)
            
        self.sign = QPushButton('Знак носителей')
        self.sign.clicked.connect(self.sign_click)
        # if not self.parent.current==2:
        #     self.sign.setEnabled(False)
        self.sign_text = QLabel('Устанавливается характер проводимости: электронный или дырочный', self)
            
        self.res = QPushButton('Удельная проводимость')
        self.res.clicked.connect(self.res_click)
        # if not self.parent.current==3:
        #     self.res.setEnabled(False)
        self.res_text = QLabel('Производится измерение оммического сопротивления образца', self)
            
        self.chart = QPushButton('Обработка данных')
        self.chart.clicked.connect(self.chart_click)
        # if not self.parent.current==4:
            # self.chart.setEnabled(False)
        self.chart_text = QLabel('Выполняется расчет всех констант образца и построение графиков', self)
                       
        self.main = QPushButton('Определение ЭДС Холла')
        self.main.clicked.connect(self.main_click)
        # if not self.parent.current==1:
        #     self.main.setEnabled(False)
        if self.parent.foldername:
            self.lineEdit.setReadOnly(True)
        self.main_text = QLabel('Определяется ЭДС Холла', self)
            
        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.setRowStretch(1, 1)
        self.hbox_layout.addWidget(self.lineEdit, 1, 0, 1, 2)
        self.hbox_layout.addWidget(self.flow, 2, 0)
        self.hbox_layout.addWidget(self.flow_text, 2, 1)
        self.hbox_layout.addWidget(self.main, 3, 0)
        self.hbox_layout.addWidget(self.main_text, 3, 1)
        self.hbox_layout.addWidget(self.sign, 4, 0)
        self.hbox_layout.addWidget(self.sign_text, 4, 1)
        self.hbox_layout.addWidget(self.res, 5, 0)
        self.hbox_layout.addWidget(self.res_text, 5, 1)
        self.hbox_layout.addWidget(self.chart, 6, 0)
        self.hbox_layout.addWidget(self.chart_text, 6, 1)

    def flow_click(self):
        self.parent.number = 10
        self.parent.change_number()
        self.parent.current+=1
        
    def chart_click(self):
        self.parent.number = 50
        self.parent.change_number()

    def main_click(self):
        self.parent.number = 20
        self.parent.change_number()
        self.parent.current+=1
        
    def res_click(self):
        self.parent.number = 40
        self.parent.change_number()
        self.parent.current+=1
        
    def sign_click(self):
        self.parent.number = 30
        self.parent.change_number()
        self.parent.current+=1

    def enter_name(self):
        # make folder
        self.parent.foldername = self.lineEdit.text()
        self.parent.folder = os.path.join(os.getcwd(), self.parent.foldername)
        if not os.path.exists(self.parent.folder):
            os.mkdir(self.parent.folder)

        self.flow.setEnabled(True)
        self.lineEdit.setReadOnly(True)
       
    def testing_analisis(self):
        self.chart.setEnabled(True)
        self.parent.foldername = 'Перерптлв'
        self.parent.folder = os.path.join(os.getcwd(), self.parent.foldername)
        if not os.path.exists(self.parent.folder):
            os.mkdir(self.parent.folder)
        self.parent.dataname = 'data.csv'
        self.parent.flow_dataname = 'Induction_data.csv'
        self.parent.a=2*10**-3
        self.parent.sigma = -313
        self.parent.sigma_sigma=0
        
        
        






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
