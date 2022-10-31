import os
import sys
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
        self.parent.foldername = self.lineEdit.text()
        self.flow.setEnabled(True)
        self.main.setEnabled(True)
        self.lineEdit.setReadOnly(True)


class MainExperiment1Window(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Основной эксперимент')
        self.start_time = 0
        self.parent = parent
        
        # make masthead
        self.dataname = 'data.txt'
        file = open(os(self.parent.foldername, self.dataname), 'w')
        file.write('I_0, mA U_34, mV t, s')
        file.close()
        
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)

        self.but = QPushButton('Измерение')
        # self.but.clicked.connect(self.but_click)
        self.setCentralWidget(self.but)

        grid_layout = QGridLayout(self)         # Create QGridLayout
        self.centralwidget.setLayout(grid_layout)   # Set this layout in central widget

        table = QTableWidget(self)  # Create a table
        table.setColumnCount(3)     #Set three columns
        table.setRowCount(1)        # and one row

          # Set the table headers
        table.setHorizontalHeaderLabels(["Header 1", "Header 2", "Header 3"])

          #Set the tooltips to headings
        table.horizontalHeaderItem(0).setToolTip("Column 1 ")
        table.horizontalHeaderItem(1).setToolTip("Column 2 ")
        table.horizontalHeaderItem(2).setToolTip("Column 3 ")
        table.setItem(0, 0, QTableWidgetItem("Text in column 1"))
        table.setItem(0, 1, QTableWidgetItem("Text in column 2"))
        table.setItem(0, 2, QTableWidgetItem("Text in column 3"))

          # Do the resize of the columns by content
        table.resizeColumnsToContents()

        grid_layout.addWidget(table, 0, 0)   # Adding the table to the grid
        grid_layout.addWidget(self.but, 0, 3)

    def but_click(self):
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
        out = open(os(self.parent.foldername, self.dataname), 'a')
        out.write(s)
        out.close()


# start = Start()
# del start


import time
import serial

ser=serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=1
)
ser.isOpen()

msg='SYSTem:REMote\n'
ser.write(msg.encode('ascii'))

while 1:

        msg='Read?\n'
        ser.write(msg.encode('ascii'))
        time.sleep(1)

        bytesToRead=ser.inWaiting()
        data=ser.read(bytesToRead)
        print(data)
