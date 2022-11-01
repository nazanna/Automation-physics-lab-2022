import os
import sys
import csv
import time
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QHBoxLayout,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QGridLayout,
    QMenu,
    QTableWidgetItem,
    QHeaderView,
    
    )


class AbstractWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.create_actions()
        self.create_menuBar()

    def create_menuBar(self):
        menuBar = self.menuBar()
        self.fileMenu = QMenu("&Файл", self)
        menuBar.addMenu(self.fileMenu)
        self.helpMenu = QMenu("&Помощь")
        menuBar.addMenu(self.helpMenu)
        self.fileMenu.addAction(self.exitAction)
        self.helpMenu.addAction(self.helpContentAction)
        self.helpMenu.addAction(self.aboutAction)

    def create_actions(self):
        self.exitAction = QAction("&Выход", self)
        self.exitAction.triggered.connect(self.exit_click)
        self.helpContentAction = QAction("&Инструкция", self)
        self.helpContentAction.triggered.connect(self.help_click)
        self.aboutAction = QAction("&О программе", self)
        self.aboutAction.triggered.connect(self.about_click)

    def exit_click(self):
        self.close()

    def help_click(self):
        print('Help')
        # TODO

    def about_click(self):
        print('About')
        # TODO


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
        if self.number == 2:
            self.window.close()
            self.window = MainExperiment1Window(self)
        if self.number == 1:
            pass
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

        self.flow = QPushButton('измерение потока')
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
        self.parent.number = 1
        self.parent.change_number()

    def main_click(self):
        self.parent.number = 2
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


class MainExperiment1Window(AbstractWindow):
    def __init__(self, parent):
        # TODO : clean code
        super().__init__()

        self.setWindowTitle('Основной эксперимент')
        self.start_time = 0
        self.parent = parent
        
        # make masthead
        self.dataname = 'data.csv'
        head_1 = 'I_0,mA'
        head_2 = 'U_34,mV'
        head_3 = 't,s'
        with open(os.path.join(self.parent.folder, self.dataname), 'w') as file:
            wr = csv.writer(file)
            wr.writerow([head_1, head_2, head_3])
        
        
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)

        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked_nodata)
        self.start.setEnabled(False)
        
        self.stop  = QPushButton('Стоп')
        self.stop.clicked.connect(self.stop_clicked)
        self.stop.setEnabled(False)

        grid_layout = QGridLayout(self.centralwidget)

        self.table = QTableWidget(self)  # Create a self.table
        self.table.setColumnCount(3)     #Set three columns
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
        
        
        self.lineEdit = QLineEdit(placeholderText='Введите что-то')
        self.lineEdit.returnPressed.connect(self.enter_smth)

        grid_layout.addWidget(self.table, 0, 0, 2, 1)   # Adding the table to the grid
        grid_layout.addWidget(self.lineEdit, 0, 2, -1, -1)
        grid_layout.addWidget(self.start, 1, 2)
        grid_layout.addWidget(self.stop, 1, 3)

        
        self.parent.draw()
    
    def enter_smth(self):
        # TODO
        self.parent.smth = self.lineEdit.text()
        self.start.setEnabled(True)
        self.lineEdit.setReadOnly(True)
        
    def start_clicked_nodata(self):
        # function to test writing data
        current_time = round(time.time()*1000)
        v = str(current_time/60)
        a=v
        t = str(current_time-self.start_time)
        with open(os.path.join(self.parent.folder, self.dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow([v, a, str(current_time-self.start_time)])
        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem(v))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(a))
        self.table.setItem(self.table.rowCount()-1, 2, QTableWidgetItem(t))
        
        self.stop.setEnabled(True)
    
    def stop_clicked(self):
        # TODO
        print('stop')
        self.stop.setEnabled(False)

    def start_click(self):
        # measure voltage and current
        volt_name = os.path.join('/dev', 'usbtmc1')
        f_volt = open(volt_name, 'w')
        f_volt.write('Measure:Voltage:DC?\n')
        f_volt.close()
        amp_name = os.path.join('/dev', 'usbtmc2')
        f_amp = open(amp_name, 'w')
        f_amp.write('Measure:Current:DC?\n')
        f_amp.close()

        f_volt = open(volt_name, 'r')
        v = f_volt.read(15)
        f_amp = open(amp_name, 'r')
        a = f_amp.read(15)
        f_volt.close()
        f_amp.close()
        current_time = round(time.time()*1000)
        s = v + a + str(current_time - self.start_time)
        with open(os.path.join(self.parent.folder, self.dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow([v, a, str(current_time-self.start_time)])

start = Start()

# =============================================================================
# import time
# import serial
# 
# ser=serial.Serial(
#     port='/dev/ttyUSB0',
#     baudrate=9600,
#     timeout=1
# )
# ser.isOpen()
# 
# msg='SYSTem:REMote\n'
# ser.write(msg.encode('ascii'))
# 
# while 1:
# 
#         msg='Read?\n'
#         ser.write(msg.encode('ascii'))
#         time.sleep(1)
# 
#         bytesToRead=ser.inWaiting()
#         data=ser.read(bytesToRead)
#         print(data)
# 
# =============================================================================
