#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 20:00:45 2022

@author: anna
"""
import os
import csv
import serial
import numpy as np
import time
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap
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
        # self.add_ser()
        self.data_thread = ThreadData(self)
        self.resize(1400, 800)
        self.number_iteration = 1
        self.start_time = 0
        self.volt = 0

        # make masthead
        self.parent.dataname = 'data.csv'
        heads = ['U_34,mV', 'I_M,mA', 'U_0,mV', 'I_0,mA', 'E, mV', 'N', 't,ms']
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'w') as file:
            wr = csv.writer(file)
            wr.writerow(heads)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)

        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(False)

        self.stop = QPushButton('Стоп')
        self.stop.clicked.connect(self.stop_clicked)
        self.stop.setEnabled(False)

        self.new = QPushButton('Новый ток')
        self.new.clicked.connect(self.new_clicked)
        self.new.setEnabled(False)

        self.chart = QPushButton('График')
        self.chart.setEnabled(False)
        self.chart.clicked.connect(self.chart_clicked)

        self.lineEdit = QLineEdit(placeholderText='Введите a, мм')
        self.lineEdit.returnPressed.connect(self.enter_a)

        # make table
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(heads))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(heads)
        header = self.table.horizontalHeader()
        for i in range(len(heads)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.table.resizeColumnsToContents()

        # Adding the table to the grid
        self.grid_layout.addWidget(self.table, 0, 0, -1, 1)
        self.grid_layout.addWidget(self.lineEdit, 0, 2, 1, -1)
        self.grid_layout.addWidget(self.start, 1, 2)
        self.grid_layout.addWidget(self.stop, 1, 3)
        self.grid_layout.addWidget(self.new, 2, 2, 1, -1)
        self.grid_layout.addWidget(self.chart, 3, 2, 1, -1)

    def add_ser(self):
        self.parent.ser = serial.Serial(
            port='/dev/ttyUSB2',
            baudrate=9600,
            timeout=1
        )
        self.parent.ser.isOpen()
        msg = 'OUTput on\n'
        self.parent.ser.write(msg.encode('ascii'))

    def enter_a(self):
        # TODO
        self.parent.a = self.lineEdit.text()
        self.start.setEnabled(True)
        self.lineEdit.setReadOnly(True)

    def start_clicked(self):
        self.stop.setEnabled(True)
        if self.start_time == 0:
            self.start_time = round(time.time()*1000)
        self.start.setEnabled(False)
        self.new.setEnabled(True)
        if not self.data_thread.running:
            self.data_thread.start()

    def stop_clicked(self):
        self.data_thread.running = False
        self.stop.setEnabled(False)
        self.start.setEnabled(True)
        self.chart.setEnabled(True)

    def new_clicked(self):
        self.number_iteration += 1
        self.volt = 0
        if not self.data_thread.running:
            self.data_thread.start()
        self.start.setEnabled(False)
        self.new.setEnabled(True)
        self.stop.setEnabled(True)

    def chart_clicked(self):
        self.parent.number = 21
        self.parent.change_number()

    def no_data(self):
        current_time = round(time.time()*1000)
        v = str((current_time-self.start_time)/60)
        t = str(current_time-self.start_time)
        if float(self.volt) <= 0.1:
            self.u_0 = v
        a = str(float(v)/100)
        I_M = v
        self.save_data([v, I_M, self.u_0, a, self.volt,
                       self.number_iteration, t])
        self.volt = str(float(self.volt)+5)
        if float(a) > 1:
            self.stop_clicked()

    def save_data(self, data):
        with open(os.path.join(self.parent.folder, self.parent.dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow(data)
        self.table.insertRow(self.table.rowCount())
        for i in range(len(data)):
            self.table.setItem(self.table.rowCount()-1, i,
                               QTableWidgetItem(str(data[i])))

    def take_data(self):
        # measure voltage and current
        msg = 'VOLTage '+str(self.volt)+'\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)

        msg = 'MEASure:Current?\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)
        bytesToRead = self.parent.ser.inWaiting()
        I_M = self.parent.ser.read(bytesToRead)
        self.volt += 5

        volt_name = os.path.join('/dev', 'usbtmc0')
        f_volt = open(volt_name, 'w')
        f_volt.write('Measure:Voltage:DC?\n')
        f_volt.close()
        amp_name = os.path.join('/dev', 'usbtmc1')
        f_amp = open(amp_name, 'w')
        f_amp.write('Measure:Current:DC?\n')
        f_amp.close()

        f_volt = open(volt_name, 'r')
        v = '{:.9f}'.format(float(f_volt.read(15))*10**3)
        if self.volt == 0:
            self.u_0 = v
        f_amp = open(amp_name, 'r')
        a = '{:.9f}'.format(float(f_amp.read(15))*10**3)
        print(a)
        # protect of errors:
        if a > 1:
            self.stop_clicked()

        f_volt.close()
        f_amp.close()

        current_time = round(time.time()*1000)
        t = str(current_time-self.start_time)

        self.save_data([v, I_M, self.u_0, a, self.volt,
                       self.number_iteration, t])

    def closeEvent(self, event):
        self.data_thread.running = False


class MainExperimentChartWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.parent = parent
        self.parent.chartname = 'Chart'
        self.parent.data = Data(data_filename=os.path.join(self.parent.folder, self.parent.dataname),
                                saving=os.path.join(self.parent.folder, self.parent.chartname))
        self.parent.data.read_csv()
        # add B(I_M) #TODO
        self.parent.data.x = np.array(self.parent.data.data['I_0,mA'])*np.array(self.parent.data.data['I_M,mA'])
        self.parent.data.y = self.parent.data.data['U_34,mV']
        self.parent.data.ylabel = 'U_34,mV'
        self.parent.data.xlabel = 'I$_{обр} \cdot B$, мА$\cdot $ Tл'
        self.parent.data.make_grafic()

        self.setWindowTitle('Основной эксперимент. Обработка данных')
        self.resize(1400, 800)

        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        pixmap = QPixmap(os.path.join(
            self.parent.folder, self.parent.chartname))
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        self.label.setFixedSize(0.7*self.width(), 0.9*self.height())
        self.label.setPixmap(pixmap)

        self.text = QTextBrowser()
        self.text.setText('text')

        self.hbox_layout = QGridLayout(self.centralwidget)
        self.hbox_layout.addWidget(self.label, 0, 0)
        self.hbox_layout.addWidget(self.text, 0, 1)
