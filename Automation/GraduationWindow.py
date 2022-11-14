#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 20:18:17 2022

@author: anna
"""

import os
import csv
import time
from PyQt6.QtWidgets import (QLineEdit,
                             QPushButton,
                             QWidget,
                             QTableWidget,
                             QGridLayout,
                             QTableWidgetItem,
                             QHeaderView,
                             )
from Abstract_window import AbstractWindow


class GraduationWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Градуировка электромагнита')
        self.parent = parent
        self.volt = 0

        # make csv file
        self.parent.flow_dataname = 'Induction_data.csv'
        self.heads = ['B,mTl', 'E,mV', 'I_M,mA','t,ms']
        with open(os.path.join(self.parent.folder, self.parent.flow_dataname), 'w') as file:
            wr = csv.writer(file)
            wr.writerow(self.heads)

        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)

        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(True)

        self.menu = QPushButton('Меню')
        self.menu.setEnabled(False)
        self.menu.clicked.connect(self.menu_clicked)

        self.lineEdit = QLineEdit(placeholderText='Индукция B, мТл')
        self.lineEdit.returnPressed.connect(self.enter_value)
        self.lineEdit.setReadOnly(True)

        self.table = QTableWidget(self)  # Create a self.table
        self.table.setColumnCount(len(self.heads))  # Set three columns
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.heads)
        header = self.table.horizontalHeader()
        for i in range(len(self.heads)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        self.table.resizeColumnsToContents()

        self.grid_layout.addWidget(self.start, 0, 0)
        self.grid_layout.addWidget(self.lineEdit, 1, 0)
        self.grid_layout.addWidget(self.table, 0, 3, -1, 1)
        self.grid_layout.addWidget(self.menu, 2, 0)

    def menu_clicked(self):
        self.parent.number = 0
        self.parent.change_number()

    def start_clicked(self):
        self.start.setEnabled(False)
        self.start_time = round(time.time()*1000)
        self.lineEdit.setReadOnly(False)
        self.menu.setEnabled(True)

    def enter_value(self):
        self.lineEdit.setReadOnly(True)
        self.no_data()
        self.lineEdit.clear()
        self.lineEdit.setReadOnly(False)
        
    def no_data(self):
        current_time = round(time.time()*1000)
        b = self.lineEdit.text()
        u = str((current_time-self.start_time)/60)
        i = str((current_time-self.start_time)/60/2)
        t = str(current_time-self.start_time)
        self.save_data([b, u, i, t])
    
    def save_data(self, data):
        with open(os.path.join(self.parent.folder, self.parent.flow_dataname), 'a') as file:
            wr = csv.writer(file)
            wr.writerow(data)
        self.table.insertRow(self.table.rowCount())
        for i in range(len(data)):
            self.table.setItem(self.table.rowCount()-1, i,
                               QTableWidgetItem(str(data[i])))

    def take_data(self):        
        t = (round(time.time()*1000)-self.start_time)
        b = self.lineEdit.text()
        msg = 'VOLTage '+str(self.volt)+'\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)

        msg = 'MEASure:Current?\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)
        bytesToRead = self.parent.ser.inWaiting()
        I_M = self.parent.ser.read(bytesToRead)
        self.volt += 5
        self.save_data([b, self.volt, I_M, t])
        
    def closeEvent(self, event):
        pass
        # msg = 'VOLTage '+str(0)+'\n'
        # self.parent.ser.write(msg.encode('ascii'))