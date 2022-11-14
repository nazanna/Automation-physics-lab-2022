#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 21:00:36 2022

@author: anna
"""
import os
import time
from PyQt6.QtWidgets import (QPushButton,
                             QWidget,
                             QGridLayout,
                             QLabel
                             )
from Abstract_window import AbstractWindow


class SignWindow(AbstractWindow):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle('Определение знака носителей')
        self.parent = parent
        
        self.start = QPushButton('Старт')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(True)

        self.menu = QPushButton('Меню')
        self.menu.setEnabled(False)
        self.menu.clicked.connect(self.menu_clicked)
        
        self.with_field = QLabel('С полем: ', self)
        self.without_field = QLabel('С полем: ', self)
        self.with_field_value = QLabel(self)
        self.without_field_value = QLabel(self)
                
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)
        
        self.grid_layout.addWidget(self.start, 0, 0, 1, -1)
        self.grid_layout.addWidget(self.with_field, 1, 0)
        self.grid_layout.addWidget(self.with_field_value, 1, 1)
        self.grid_layout.addWidget(self.without_field, 2, 0)
        self.grid_layout.addWidget(self.without_field_value, 2, 1)
        self.grid_layout.addWidget(self.menu, 3, 0, 1, -1)
        
    def menu_clicked(self):
        self.parent.number = 0
        self.parent.change_number()

    def start_clicked(self):
        self.start.setEnabled(False)
        with_field=10
        without_field=15
        # without_field, with_field = self.get_values()
        self.with_field_value.setText(str(with_field)+', mV')
        self.without_field_value.setText(str(without_field)+', mV')
        self.menu.setEnabled(True)
        
    def measure(self, volt):
        msg = 'VOLTage '+str(volt)+'\n'
        self.parent.ser.write(msg.encode('ascii'))
        time.sleep(1)
        f_volt = open(self.parent.volt_name, 'w')
        f_volt.write('Measure:Voltage:DC?\n')
        f_volt.close()
        f_volt = open(self.parent.volt_name, 'r')
        v = '{:.9f}'.format(float(f_volt.read(15))*10**3)
        f_volt.close()
        return v
    
    def get_values(self):
        without_field = self.measure(0)
        with_field = self.measure(10)
        return without_field, with_field
        
    def closeEvent(self, event):
        pass
        # msg = 'VOLTage '+str(0)+'\n'
        # self.parent.ser.write(msg.encode('ascii'))