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
                             QTableWidget,
                             QGridLayout,
                             QTableWidgetItem,
                             QHeaderView,
                             )
from Abstract_window import AbstractWindow
from Main_experiment_window import (MainExperimentDataWindow,
                                    MainExperimentChartWindow)


class Start:
    def __init__(self):
        self.number = 0
        self.foldername = ''
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        self.window = StartWindow(self)
        self.draw()
        self.app.exec()

    def __del__(self):
        print('destruct')

    def draw(self):
        self.window.show()

    def change_number(self):
        if self.number == 20:
            self.window.close()
            self.window = MainExperimentDataWindow(self)
        if self.number == 21:
            self.window.close()
            self.window = MainExperimentChartWindow(self)
        if self.number == 10:
            self.window.close()
            self.window = FlowWindow(self)
        if self.number == 0:
            self.window.close()
            self.window = StartWindow(self)
        self.draw()


class StartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Эффект Холла в полупроводниках')
        self.parent = parent
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        self.lineEdit = QLineEdit(placeholderText='Введите фамилию')
        self.lineEdit.returnPressed.connect(self.enter_name)

        self.flow = QPushButton('градуировка электромагнита')
        self.flow.clicked.connect(self.flow_click)
        self.flow.setEnabled(False)
        self.main = QPushButton('основной эксперимент')
        self.main.clicked.connect(self.main_click)
        self.main.setEnabled(False)

        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.setRowStretch(1, 1)
        self.hbox_layout.addWidget(self.lineEdit, 1, 0, 1, 2)
        self.hbox_layout.addWidget(self.flow, 2, 0)
        self.hbox_layout.addWidget(self.main, 2, 1)

    def flow_click(self):
        self.parent.number = 10
        self.parent.change_number()

    def main_click(self):
        self.parent.number = 20
        self.parent.change_number()

    def enter_name(self):
        # make folder
        self.parent.foldername = self.lineEdit.text()
        self.parent.folder = os.path.join(os.getcwd(), self.parent.foldername)
        if not os.path.exists(self.parent.folder):
            os.mkdir(self.parent.folder)

        self.flow.setEnabled(True)
        self.main.setEnabled(True)
        self.lineEdit.setReadOnly(True)


class FlowWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()
        
        self.setWindowTitle('Градуировка электромагнита')
        self.parent = parent
        
        
        # make csv file
        self.parent.flow_dataname = 'Induction_data.csv'
        head_1 = 'B,mTl'
        head_2 = 'U,mV'
        head_3 = 't,ms'
        with open(os.path.join(self.parent.folder, self.parent.flow_dataname), 'w') as file:
            wr = csv.writer(file)
            wr.writerow([head_1, head_2, head_3])
            
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)

        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(True)
        
        self.next = QPushButton(self)
        self.next.setIcon(QIcon('arrow.png'))
        self.next.setEnabled(False)
        self.next.clicked.connect(self.next_clicked)

        self.lineEdit = QLineEdit(placeholderText='Индукция B, мТл')
        self.lineEdit.returnPressed.connect(self.enter_value)
        self.lineEdit.setReadOnly(True)

        self.table = QTableWidget(self)  # Create a self.table
        self.table.setColumnCount(3)  # Set three columns
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([head_1, head_2, head_3])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setItem(0, 0, QTableWidgetItem("Text in column 1"))
        self.table.setItem(0, 1, QTableWidgetItem("Text in column 2"))
        self.table.setItem(0, 2, QTableWidgetItem("Text in column 3"))
        self.table.resizeColumnsToContents()
        
        self.grid_layout.addWidget(self.start, 0, 0)
        self.grid_layout.addWidget(self.lineEdit, 1, 0)
        self.grid_layout.addWidget(self.table, 1, 3)
        self.grid_layout.addWidget(self.next, 2, 0)
    
    def next_clicked(self):
        self.parent.number = 20
        self.parent.change_number()

    def start_clicked(self):
        self.start.setEnabled(False)
        self.start_time = round(time.time()*1000)
        self.lineEdit.setReadOnly(False)
        self.next.setEnabled(True)

    def enter_value(self):
        self.lineEdit.setReadOnly(True)
        self.get_data()
        self.lineEdit.clear()
        self.lineEdit.setReadOnly(False)

    def get_data(self):
        
        
       
        # bytesToRead=ser.inWaiting()
        # data=ser.read(bytesToRead)
        # print(data)
                
        current_time = round(time.time()*1000)
        b = self.lineEdit.text()
        u = str((current_time-self.start_time)/60)
        t = str(current_time-self.start_time)
        with open(os.path.join(self.parent.folder, self.parent.flow_dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow([b, u, str(t)])
        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem(b))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(u))
        self.table.setItem(self.table.rowCount()-1, 2, QTableWidgetItem(t))



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

