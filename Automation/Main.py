import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time
import pandas as pd
from PyQt6 import QtCore
from PyQt6.QtGui import QAction,  QIcon, QPixmap
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
                             QTextBrowser,
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
        if self.number == 20:
            self.window.close()
            self.window = MainExperimentDataWindow(self)
        if self.number == 21:
            self.window.close()
            self.window = MainExperimentChartWindow(self)

        if self.number == 10:
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


class ThreadData(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.running = False
        self.parent = parent

    def run(self):
        self.running = True
        while self.running:
            self.parent.no_data()
            self.sleep(1)


class MainExperimentDataWindow(AbstractWindow):
    def __init__(self, parent):
        # TODO : clean code
        super().__init__()

        self.setWindowTitle('Основной эксперимент. Получение данных')
        self.start_time = round(time.time()*1000)
        self.parent = parent
        self.data_thread = ThreadData(self)
        self.resize(1400, 800)

        # make masthead
        self.parent.dataname = 'data.csv'
        head_1 = 'I_0,mA'
        head_2 = 'U_34,mV'
        head_3 = 't,s'
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'w') as file:
            wr = csv.writer(file)
            wr.writerow([head_1, head_2, head_3])

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(False)

        self.stop = QPushButton('Стоп')
        self.stop.clicked.connect(self.stop_clicked)
        self.stop.setEnabled(False)

        self.next = QPushButton(self)
        self.next.setIcon(QIcon('arrow.png'))
        self.next.setEnabled(False)
        self.next.clicked.connect(self.next_clicked)

        grid_layout = QGridLayout(self.centralwidget)

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

        self.lineEdit = QLineEdit(placeholderText='Введите что-то')
        self.lineEdit.returnPressed.connect(self.enter_smth)

        # Adding the table to the grid
        grid_layout.addWidget(self.table, 0, 0, -1, 1)
        grid_layout.addWidget(self.lineEdit, 0, 2, -1, -1)
        grid_layout.addWidget(self.next, 2, 2, -1, -1)
        grid_layout.addWidget(self.start, 1, 2)
        grid_layout.addWidget(self.stop, 1, 3)

        self.parent.draw()

    def enter_smth(self):
        # TODO
        self.parent.smth = self.lineEdit.text()
        self.start.setEnabled(True)
        self.lineEdit.setReadOnly(True)

    def start_clicked(self):
        self.stop.setEnabled(True)
        self.start.setEnabled(False)
        if not self.data_thread.isRunning():
            self.data_thread.start()

    def no_data(self):
        current_time = round(time.time()*1000)
        v = str((current_time-self.start_time)/60)
        a = v
        t = str(current_time-self.start_time)
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow([v, a, str(current_time-self.start_time)])
        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem(v))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(a))
        self.table.setItem(self.table.rowCount()-1, 2, QTableWidgetItem(t))

    def stop_clicked(self):
        self.data_thread.running = False
        self.stop.setEnabled(False)
        self.next.setEnabled(True)

    def next_clicked(self):
        self.parent.number = 21
        self.parent.change_number()

    def take_data(self):
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
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow([v, a, str(current_time-self.start_time)])


class MainExperimentChartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.parent.chartname = 'Chart'
        self.parent.data = Data(data_filename=os.path.join(self.parent.folder, self.parent.dataname), 
                                saving=os.path.join(self.parent.folder, self.parent.chartname))
        self.parent.data.read_csv()
        self.parent.data.x=self.parent.data.data['I_0,mA']
        self.parent.data.y=self.parent.data.data['U_34,mV']
        self.parent.data.make_grafic()
        
        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.resize(1400, 800)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        pixmap = QPixmap(os.path.join(self.parent.folder, self.parent.chartname))
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())

        self.text = QTextBrowser()
        self.text.setText('text')

        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.addWidget(self.label, 0, 0)
        self.hbox_layout.addWidget(self.text, 0, 1)





class Data:
    def __init__(self, x=[], y=[], xlabel='', ylabel='', caption='', xerr=None, 
                 yerr=None, through_0=0, data_filename='', color=None, 
                 centering=None, size=15, coefficient=[0.9, 1.1], saving=None):
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.caption = caption
        self.xerr=xerr
        self.yerr=yerr
        self.make_errors(xerr, yerr)
        self.through_0 = through_0
        if not color:
            self.color = ['limegreen', 'indigo']
        else:
            self.color = color
        self.centering = centering
        self.size = size
        self.coefficient = coefficient
        self.data_filename=data_filename
        self.saving=saving
        
    def make_errors(self, xerr=None, yerr=None):
        if not xerr: xerr=self.xerr
        if not yerr: yerr=self.yerr
        if not xerr: xerr=0
        if not yerr: yerr=0
        if not yerr or type(yerr) == float or type(yerr) == int:
            self.yerr = [yerr for _ in self.y]
        else: 
            self.yerr = yerr
        if not xerr or type(xerr) == float or type(xerr) == int:
            self.xerr = [xerr for _ in self.x]
        else: 
            self.xerr = xerr
    
    def read_csv(self):
        with open(self.data_filename) as file:
            reader = list(csv.reader(file))
        data = np.array(reader)
        dic=[]
        for i in range(len(data[0])):
            micro_data = []
            for j in range(len(data)):
                micro_data.append(data[j][i])
            dic.append(micro_data)
        data=dic
        dic = {}
        for i in range(len(data)):
            dic[data[i][0]] = np.array(data[i][1:]).astype(np.float)
        data = dic
        self.data=data

    def make_point_grafic(self):
        self.make_errors()
        if self.xerr[1] != 0 or self.yerr[1] != 0:
            plt.errorbar(self.x, self.y, yerr=self.yerr, xerr=self.xerr, linewidth=4,
                         linestyle='', label=self.caption, color=self.color[0],
                         ecolor=self.color[0], elinewidth=1, capsize=3.4,
                         capthick=1.4)
        else:
            plt.scatter(self.x, self.y, linewidth=0.005, label=self.caption,
                        color=self.color[0], edgecolor='black', s=self.size)

        if not self.centering:
            plt.xlabel(self.xlabel)
            plt.ylabel(self.ylabel)
        else:
            self.ax = plt.gca()
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['bottom'].set_position('zero')
            self.ax.spines['left'].set_position('zero')
            self.ax.set_xlabel(self.ylabel, labelpad=-180, fontsize=14)
            self.ax.set_ylabel(self.xlabel, labelpad=-260,
                               rotation=0, fontsize=14)

    def make_line_grafic(self, k, b):
        if min(self.x) > 0:
            xmin = min(self.x)*self.coefficient[0]
        else:
            xmin = min(self.x)*self.coefficient[1]

        if max(self.x) > 0:
            xmax = max(self.x)*self.coefficient[1]
        else:
            xmax = max(self.x)*self.coefficient[0]
        x = np.arange(xmin, xmax, (xmax-xmin)/10000)
        plt.plot(x, k*x+b, label=self.caption, linewidth=2.4,
                 linestyle='-', color=self.color[1])

    def make_grafic(self, named_by_points=True):        
        self.make_errors()
        if named_by_points:
            cap_point = self.caption
            line_point = None
        else:
            line_point = self.caption
            cap_point = None
        self.make_point_grafic()
        
        k, b, sigma = self.approx()
        sigma[0] = abs(k*((sigma[0]/k)**2+(np.mean(self.yerr)/np.mean(self.y))**2 +
                          (np.mean(self.xerr)/np.mean(self.x))**2)**0.5)
        if (b != 0):
            sigma[1] = abs(b*((sigma[1]/b)**2+(np.mean(self.yerr)/np.mean(self.y))**2 +
                              (np.mean(self.xerr)/np.mean(self.x))**2)**0.5)
        else:
            sigma[1] = 0

        self.make_line_grafic(k, b)
        plt.legend()
        if self.saving:
            plt.savefig(self.saving)
        return k, b, sigma

    def approx(self):
        if self.yerr[0] != 0:
            sigma_y = [1/i**2 for i in self.y]
        else:
            sigma_y = np.array([1 for _ in self.y])
        if self.through_0 == 0:
            def f(x, k):
                return k*x
            k, sigma = curve_fit(f, xdata=self.x, ydata=self.y, sigma=sigma_y)
            sigma = np.sqrt(np.diag(sigma))
            return k[0], 0, [sigma[0], 0]
        else:
            def f(x, k, b):
                return x*k + b
            k, sigma = curve_fit(f, xdata=self.x, ydata=self.y, sigma=sigma_y)
            sigma_b = np.sqrt(sigma[1][1])
            b = k[1]
            k = k[0]
            sigma = np.sqrt(sigma[0][0])
            return k, b, [sigma, sigma_b]


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
