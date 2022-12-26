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
                             QTextBrowser,
                             QDialog,
                             QDialogButtonBox,
                             QVBoxLayout
                             )
from PyQt5.QtWidgets import QMessageBox
from Analisis_data import Data
from Abstract_window import AbstractWindow


class ThreadData(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.running = False
        self.parent = parent

    def run(self):
        self.running = True
        while self.running:
            self.parent.take_data()
            self.sleep(1)

class ThreadWarning(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self)
        self.running = False
        self.parent = parent
        
    def run(self):
        self.running = True
        while self.running:
            self.sleep(1)
            self.dlg.show()




class MainWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Определение ЭДС Холла')
        self.parent = parent
    
        self.data_thread = ThreadData(self)
        # self.thread = ThreadWarning(self)
        self.resize(1400, 800)
        self.number_iteration = 1
        self.start_time = 0
        self.volt = 0
        self.U_0={}

        # make masthead
        self.parent.dataname = 'data.csv'
        heads = ['U_34,mV', 'I_M,mA', 'U_0,mV', 'I_0,mA', 'E,mV', 'N', 't,ms']
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

        self.new = QPushButton('Новое напряжение')
        self.new.clicked.connect(self.new_clicked)
        self.new.setEnabled(False)

        self.menu = QPushButton('Меню')
        self.menu.setEnabled(False)
        self.menu.clicked.connect(self.menu_clicked)

        self.lineEdit = QLineEdit(placeholderText='Введите a, мм')
        self.lineEdit.returnPressed.connect(self.enter_a)

        # make table
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(heads))
        self.table.setRowCount(0)
        
        rowPosition = self.table.rowCount()
        it = QTableWidgetItem(str(rowPosition))
        self.table.setHorizontalHeaderLabels(heads)
        header = self.table.horizontalHeader()
        for i in range(len(heads)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.table.resizeColumnsToContents()
        self.table.scrollToItem(it)   

        # Adding the table to the grid
        self.grid_layout.addWidget(self.table, 1, 0, -1, 1)
        self.grid_layout.addWidget(self.lineEdit, 1, 2, 1, -1)
        self.grid_layout.addWidget(self.start, 2, 2)
        self.grid_layout.addWidget(self.stop, 2, 3)
        self.grid_layout.addWidget(self.new, 3, 2, 1, -1)
        self.grid_layout.addWidget(self.menu, 4, 2, 1, -1)

    def enter_a(self):
        self.parent.a = float(self.lineEdit.text())/10**3
        self.start.setEnabled(True)
        self.lineEdit.setReadOnly(True)

    def start_clicked(self):
        self.stop.setEnabled(True)
        if self.start_time == 0:
            self.start_time = round(time.time()*1000)
            self.this_time = self.start_time
        self.start.setEnabled(False)
        self.new.setEnabled(True)
        if not self.data_thread.running:
            self.data_thread.start()

    def stop_clicked(self):
        self.data_thread.running = False
        self.stop.setEnabled(False)
        self.start.setEnabled(True)
        self.menu.setEnabled(True)

    def new_clicked(self):
        self.number_iteration += 1
        self.volt = 0
        self.this_time = round(time.time()*1000)
        if not self.data_thread.running:
            self.data_thread.start()
        self.start.setEnabled(False)
        self.new.setEnabled(True)
        self.stop.setEnabled(True)

    def menu_clicked(self):
        self.parent.number = 0
        self.parent.change_number()

    def no_data(self):
        current_time = round(time.time()*1000)
        v = str((current_time-self.start_time)/60)
        t = str(current_time-self.start_time)
        self.u_0 = v
        a = str(float(v)/10)
        I_M = v
        self.save_data([v, I_M, self.u_0, a, self.volt,
                       self.number_iteration, t])
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
        self.table.scrollToBottom()

    def take_data(self):
        
        current_time = round(time.time()*1000)
        t = str(current_time-self.start_time)
        
        # measure voltage and current
        msg = 'VOLTage '+str(self.volt)+'\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)
        
        amps=[]
        volts=[]
        i_ms=[]
        for i in range(5):
            time.sleep(1)
            f_amp = open(self.parent.I_M_name, 'w')
            f_amp.write('Measure:Current:DC?\n')
            f_amp.close()
    
            f_volt = open(self.parent.volt_name, 'w')
            f_volt.write('Measure:Voltage:DC?\n')
            f_volt.close()
            f_amp = open(self.parent.amp_name, 'w')
            f_amp.write('Measure:Current:DC?\n')
            f_amp.close()
            time.sleep(1)
            
            f_amp = open(self.parent.I_M_name, 'r')
            I_M = '{:.9f}'.format(float(f_amp.read(15))*10**3)
            f_amp.close()
    
            f_volt = open(self.parent.volt_name, 'r')
            v = '{:.9f}'.format(float(f_volt.read(15))*10**3)
            try:
                self.u_0 = self.U_0[self.volt]
            except KeyError:
                self.U_0[self.volt] = v
                self.u_0 = self.U_0[self.volt]
            
            f_amp = open(self.parent.amp_name, 'r')
            a = '{:.9f}'.format(float(f_amp.read(15))*10**3)
            # protect of errors:
            if float(a) > 1 or self.table.rowCount()>=20*self.number_iteration:
                self.stop_clicked()
    
            f_volt.close()
            f_amp.close()
            amps.append(float(a))
            i_ms.append(float(I_M))
            volts.append(float(v))
        amps=np.array(amps)
        i_ms=np.array(i_ms)
        volts=np.array(volts)
        print(amps, i_ms, volts)
        I_M = np.mean(i_ms)
        v= np.mean(volts)
        a=np.mean(amps)
        self.save_data([v, I_M, self.u_0, a, self.volt,
                       self.number_iteration, t])
        self.volt += 0.05


    def closeEvent(self, event):
        self.data_thread.running = False
        self.parent.close()



