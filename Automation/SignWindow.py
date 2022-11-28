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
        
        self.start = QPushButton('Без поля')
        self.start.clicked.connect(self.start_clicked)
        self.start.setEnabled(True)

        self.menu = QPushButton('Меню')
        self.menu.setEnabled(False)
        self.menu.clicked.connect(self.menu_clicked)
        
        self.field = QPushButton('С полем')
        self.field.setEnabled(False)
        self.field.clicked.connect(self.field_clicked)
        
        self.with_field = QLabel('С полем: ', self)
        self.without_field = QLabel('Без поля: ', self)
        self.with_field_value = QLabel(self)
        self.without_field_value = QLabel(self)
                
        self.centralwidget = QWidget()
        self.resize(1400, 800)
        self.setCentralWidget(self.centralwidget)
        self.grid_layout = QGridLayout(self.centralwidget)
        
        self.grid_layout.addWidget(self.start, 0, 0, 1, -1)
        self.grid_layout.addWidget(self.without_field, 1, 0)
        self.grid_layout.addWidget(self.without_field_value, 1, 1)
        
        self.grid_layout.addWidget(self.field, 2, 0, 1, -1)
        self.grid_layout.addWidget(self.with_field, 3, 0)
        self.grid_layout.addWidget(self.with_field_value, 3, 1)
        
        self.grid_layout.addWidget(self.menu, 4, 0, 1, -1)
        
    def menu_clicked(self):
        self.parent.number = 0
        self.parent.change_number()

    def start_clicked(self):
        self.start.setEnabled(False)
        without_field=10
        without_field = self.measure()
        self.without_field_value.setText(str(without_field)+', mV')
        self.field.setEnabled(True)
        
    def field_clicked(self):
        with_field=90
        
        
        with_field = self.measure()
        self.with_field_value.setText(str(with_field)+', mV')
        self.menu.setEnabled(True)
        
        
    def measure(self):
        f_volt = open(self.parent.volt_name, 'w')
        f_volt.write('Measure:Voltage:DC?\n')
        f_volt.close()
        f_volt = open(self.parent.volt_name, 'r')
        v = '{:.9f}'.format(float(f_volt.read(15))*10**3)
        f_volt.close()
        return v
    
        
    def closeEvent(self, event):
        self.parent.close()