#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 20:00:45 2022

@author: anna
"""
import os
import csv
import time
from PyQt6 import QtCore
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QLabel,
                             QLineEdit,
                             QPushButton,
                             QWidget,
                             QTableWidget,
                             QGridLayout,
                             QTableWidgetItem,
                             QHeaderView,
                             QTextBrowser)
from Analisis_data import Data
from Abstract_window import AbstractWindow


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
        super().__init__()

        self.setWindowTitle('Основной эксперимент. Получение данных')
        self.parent = parent
        self.data_thread = ThreadData(self)
        self.resize(1400, 800)

        # make masthead
        self.parent.dataname = 'data.csv'
        head_1 = 'I_0,mA'
        head_2 = 'U_34,mV'
        head_3 = 't,ms'
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'w') as file:
            wr = csv.writer(file)
            wr.writerow([head_1, head_2, head_3])

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)

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

        self.lineEdit = QLineEdit(placeholderText='Введите что-то')
        self.lineEdit.returnPressed.connect(self.enter_smth)

        # make table
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([head_1, head_2, head_3])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.resizeColumnsToContents()

        # Adding the table to the grid
        self.grid_layout.addWidget(self.table, 0, 0, -1, 1)
        self.grid_layout.addWidget(self.lineEdit, 0, 2, -1, -1)
        self.grid_layout.addWidget(self.next, 2, 2, -1, -1)
        self.grid_layout.addWidget(self.start, 1, 2)
        self.grid_layout.addWidget(self.stop, 1, 3)

    def enter_smth(self):
        # TODO
        self.parent.smth = self.lineEdit.text()
        self.start.setEnabled(True)
        self.lineEdit.setReadOnly(True)

    def start_clicked(self):
        self.stop.setEnabled(True)
        self.start_time = round(time.time()*1000)
        self.start.setEnabled(False)
        if not self.data_thread.isRunning():
            self.data_thread.start()

    def stop_clicked(self):
        self.data_thread.running = False
        self.stop.setEnabled(False)
        self.next.setEnabled(True)

    def next_clicked(self):
        self.parent.number = 21
        self.parent.change_number()

    def no_data(self):
        current_time = round(time.time()*1000)
        v = str((current_time-self.start_time)/60)
        a = v
        t = str(current_time-self.start_time)
        self.save_data(v, a, t)

    def save_data(self, v, a, t):
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow([v, a, t])
        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount()-1, 0, QTableWidgetItem(v))
        self.table.setItem(self.table.rowCount()-1, 1, QTableWidgetItem(a))
        self.table.setItem(self.table.rowCount()-1, 2, QTableWidgetItem(t))

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
        t = str(current_time-self.start_time)
        self.save_data(v, a, t)


class MainExperimentChartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.parent = parent
        self.parent.chartname = 'Chart'
        self.parent.data = Data(data_filename=os.path.join(self.parent.folder, self.parent.dataname),
                                saving=os.path.join(self.parent.folder, self.parent.chartname))
        self.parent.data.read_csv()
        self.parent.data.x = self.parent.data.data['I_0,mA']
        self.parent.data.y = self.parent.data.data['U_34,mV']
        self.parent.data.make_grafic()

        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.resize(1400, 800)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        pixmap = QPixmap(os.path.join(
            self.parent.folder, self.parent.chartname))
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())

        self.text = QTextBrowser()
        self.text.setText('text')

        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.addWidget(self.label, 0, 0)
        self.hbox_layout.addWidget(self.text, 0, 1)
